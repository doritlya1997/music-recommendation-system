from functools import partial

import pandas
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from tempfile import TemporaryDirectory
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import window
from pyspark.sql import functions as F
import pandas as pd
from pyspark.ml.feature import MinMaxScaler, VectorAssembler
from pyspark.ml.functions import vector_to_array
import secrets1


def config_spark():
    tmpdir = TemporaryDirectory()
    builder = (
        SparkSession.builder.master("local[*]")
        .config("spark.jars", "./jar/postgresql-42.7.3.jar")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", f"file:///{tmpdir.name}")
        .config("spark.executor.memory", "4g")  # Increase executor memory
        .config("spark.driver.memory", "4g")    # Increase driver memory
    )

    return configure_spark_with_delta_pip(builder).getOrCreate()


def get_genres(spark: SparkSession):
    songs_df = spark.read.csv('data/spotify_data.csv', header=True, inferSchema=True)
    songs_df.select("genre").distinct() \
        .write.csv('./genres.csv')


def get_empty_popularity_loudness_tempo(spark: SparkSession):
    songs_df = spark.read.csv('data/spotify_data.csv', header=True, inferSchema=True)
    songs_df \
        .where(F.col('popularity').isNull() | F.col('loudness').isNull() | F.col('tempo').isNull()) \
        .show()
        # .write.csv('./empty_popularity_loudness_tempo.csv')


def get_years(spark: SparkSession):
    songs_df = spark.read.csv('data/spotify_data.csv', header=True, inferSchema=True)
    songs_df.select("year").distinct() \
        .write.csv('./years.csv')


def get_track_id_counts(spark: SparkSession):
    songs_df = spark.read.csv('data/spotify_data.csv', header=True, inferSchema=True)
    songs_df.groupBy("track_id").count() \
        .filter("count > 1") \
        .write.csv('./dup_track_id.csv', header=True)


def drop_duplicate_track_id_songs(spark: SparkSession):
    songs_df = spark.read.csv('data/spotify_data.csv', header=True, inferSchema=True)
    duplicate_track_id_df = spark.read.csv('./dup_track_id.csv/', header=True, inferSchema=True)

    songs_df.join(duplicate_track_id_df, ["track_id"], "leftanti") \
        .write.csv('./data_no_duplicates.csv', header=True)


def process_data_write_csv_with_pandas(spark: SparkSession):
    from pyspark.sql import SparkSession
    # from sklearn.preprocessing import MinMaxScaler

    schemaaa = schema = """
    track_id STRING,
    id INT,
    artist_name STRING,
    track_name STRING,
    popularity INT,
    year INT,
    genre STRING,
    danceability FLOAT,
    energy FLOAT,
    key INT,
    loudness FLOAT,
    mode INT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    duration_ms INT,
    time_signature INT
    """

    # Read from a stream source, e.g., Kafka (you can adjust this to your source)
    songs_df = spark.readStream.csv('./data_no_duplicates.csv/', header=True, schema=schemaaa)

    # Function to process each batch
    def process_batch(df, epoch_id):
        # Convert Spark DataFrame to Pandas DataFrame for further processing
        pandas_df = df.toPandas()

        # Pandas processing
        pandas_df['year'] = pandas_df['year'].fillna(0).astype(int)

        # make buckets based on year range to match feature vector
        pandas_df['year_2000-2004'] = pandas_df['year'].astype(int).apply(lambda year: 1 if year>=2000 and year<2005 else 0)
        pandas_df['year_2005-2009'] = pandas_df['year'].astype(int).apply(lambda year: 1 if year>=2005 and year<2010 else 0)
        pandas_df['year_2010-2014'] = pandas_df['year'].astype(int).apply(lambda year: 1 if year>=2010 and year<2015 else 0)
        pandas_df['year_2015-2019'] = pandas_df['year'].astype(int).apply(lambda year: 1 if year>=2015 and year<2020 else 0)
        pandas_df['year_2020-2024'] = pandas_df['year'].astype(int).apply(lambda year: 1 if year>=2020 and year<2025 else 0)
        pandas_df = pandas_df.drop(columns=['year'])

        # sort alphabetical order to match columns with feat_vec df
        # pandas_df = pandas_df.sort_index(axis=1)

        # pandas_df_artist_name_col = pandas_df['artist_name']
        # pandas_df_genre_col = pandas_df['genre']
        # pandas_df_track_name_col = pandas_df['track_name']
        # columns_to_drop = ['artist_name', 'genre', 'track_name']
        # pandas_df = pandas_df.drop(columns=columns_to_drop)

        # change scale to match scale of feature vector playlist
        # popularity scale: 1-100, loudness scale: -60-0, tempo scale: 0-250, scale features from 0-1
        # add min and max values for each row to establish min and max values, then once scaling is done, remove min and max columns
        min_row = {'popularity': '0', 'loudness': '-60', 'tempo': '0'}
        max_row = {'popularity': '100', 'loudness': '0', 'tempo': '250'}

        pandas_df = pandas_df._append(min_row, ignore_index=True)
        pandas_df = pandas_df._append(max_row, ignore_index=True)

        # scale popularity, loudness, and tempo features to 0-1
        scale = ['popularity', 'loudness', 'tempo']
        scaler = MinMaxScaler()
        pandas_df[scale] = scaler.fit_transform(pandas_df[scale])

        # drop min and max values
        pandas_df = pandas_df.iloc[:-2]

        # pandas_df = pandas_df.sort_index(axis=1)

        # Save the Pandas DataFrame to a CSV file
        # csv_file_path = f"./data_ready_for_db.csv/batch_{epoch_id}.csv"
        # pandas_df.to_csv(csv_file_path, index=False)

        spark.conf.set("spark.sql.execution.arrow.enabled","true")
        spark_df = spark.createDataFrame(pandas_df)
        # spark_df.printSchema()
        # spark_df.show()
        spark_df.write.csv(f"./data_ready_for_db.csv", header=True)

    # Apply the process_batch function to each batch
    songs_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .start() \
        .awaitTermination()


def process_data_write_csv_just_spark(spark: SparkSession):

    # Function to process each batch
    def process_batch(feat_vec, epoch_id):
        # Convert Spark DataFrame to Pandas DataFrame for further processing
        # pandas_df = df.toPandas()

        # Pandas processing
        # pandas_df['year'] = pandas_df['year'].fillna(0).astype(int)
        feat_vec = feat_vec.fillna(0, subset='year') \
            .withColumn('year_2000_2004', F.when(F.col('year').between(2000, 2004), 1).otherwise(0)) \
            .withColumn('year_2005_2009', F.when(F.col('year').between(2005, 2009), 1).otherwise(0)) \
            .withColumn('year_2010_2014', F.when(F.col('year').between(2010, 2014), 1).otherwise(0)) \
            .withColumn('year_2015_2019', F.when(F.col('year').between(2015, 2019), 1).otherwise(0)) \
            .withColumn('year_2020_2024', F.when(F.col('year').between(2020, 2024), 1).otherwise(0)) \
            # .drop('year')

        # all_columns = ['track_id', '_c0', 'artist_name', 'track_name', 'popularity', 'year', 'genre', 'danceability',
        #                'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
        #                'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
        scale_columns = ['popularity', 'loudness', 'tempo']
        min_row = Row(popularity=0, loudness=-60, tempo=0)
        max_row = Row(popularity=100, loudness=0, tempo=250)

        # min_row = Row(**{col1: 0 for col1 in all_columns})
        # max_row = Row(**{col1: 0 for col1 in all_columns})

        # Convert min_row and max_row to DataFrames
        min_row_df = spark.createDataFrame([min_row])
        max_row_df = spark.createDataFrame([max_row])

        min_row_df = min_row_df.withColumn('popularity', lit(0)) \
            .withColumn('loudness', lit(-60)) \
            .withColumn('tempo', lit(0))

        max_row_df = max_row_df.withColumn('popularity', lit(100)) \
            .withColumn('loudness', lit(0)) \
            .withColumn('tempo', lit(250))

        feat_vec = feat_vec.where(F.col('popularity').isNotNull() &
                                  F.col('loudness').isNotNull() &
                                  F.col('tempo').isNotNull())

        # feat_vec = feat_vec.union(min_row_df).union(max_row_df)
        feat_vec = feat_vec.unionByName(min_row_df, allowMissingColumns=True) \
            .unionByName(max_row_df, allowMissingColumns=True)

        # Assemble all columns into a single feature vector
        assembler = VectorAssembler(inputCols=scale_columns, outputCol="features")
        feat_vec = assembler.transform(feat_vec)

        # Scale the features
        scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
        scaler_model = scaler.fit(feat_vec)
        feat_vec = scaler_model.transform(feat_vec)

        feat_vec = feat_vec.filter(
            (col("popularity") != 0) & (col("popularity") != 100) &
            (col("loudness") != -60) & (col("loudness") != 0) &
            (col("tempo") != 0) & (col("tempo") != 250)
        )

        # Extract the scaled features back into separate columns
        for i, col_name in enumerate(scale_columns):
            feat_vec = feat_vec.withColumn(col_name, vector_to_array(col("scaled_features")).getItem(i))

        feat_vec = feat_vec.drop('features', 'scaled_features')

        # add min and max values for each row to establish min and max values, then once scaling is done, remove min and max columns
        #             min_row = {'popularity': '0', 'loudness': '-60', 'tempo': '0'}
        #             max_row = {'popularity': '100', 'loudness': '0', 'tempo': '250'}
        #
        #             pandas_df = pandas_df._append(min_row, ignore_index=True)
        #             pandas_df = pandas_df._append(max_row, ignore_index=True)
        #
        #             # scale popularity, loudness, and tempo features to 0-1
        #             scale = ['popularity', 'loudness', 'tempo']
        #             scaler = MinMaxScaler()
        #             pandas_df[scale] = scaler.fit_transform(pandas_df[scale])
        #
        #             # drop min and max values
        #             pandas_df = pandas_df.iloc[:-2]


        # pandas_df = pandas_df.sort_index(axis=1)

        # Save the Pandas DataFrame to a CSV file
        # csv_file_path = f"./data_ready_for_db.csv/batch_{epoch_id}.csv"
        # pandas_df.to_csv(csv_file_path, index=False)

        # spark.conf.set("spark.sql.execution.arrow.enabled","true")
        # spark_df = spark.createDataFrame(pandas_df)
        # spark_df.printSchema()
        # spark_df.show()
        feat_vec.write.mode("overwrite").parquet(f"./data_ready_for_db_parquet2")

    schemaaa = """
    track_id STRING, id INT, artist_name STRING, track_name STRING, popularity INT, year INT, genre STRING, danceability FLOAT, energy FLOAT, key INT, loudness FLOAT, mode INT, speechiness FLOAT, acousticness FLOAT, instrumentalness FLOAT, liveness FLOAT, valence FLOAT, tempo FLOAT, duration_ms INT, time_signature INT
    """

    # Read from a stream source, e.g., Kafka (you can adjust this to your source)
    spark.readStream \
        .csv('./data_no_duplicates.csv/', header=True, schema=schemaaa) \
        .writeStream \
        .foreachBatch(process_batch) \
        .trigger(availableNow=True) \
        .start() \
        .awaitTermination()


def validate_result(spark):
    # result_df = (spark.read.parquet("./data_ready_for_db.csv", header=True, inferSchema=True))
    result_df = (spark.read.parquet("./data_ready_for_db_parquet2"))

    print(result_df.count())  # 999,401 records
    print(result_df.schema)
    # |-- track_id: string (nullable = true)
    # |-- id: integer (nullable = true)
    # |-- artist_name: string (nullable = true)
    # |-- track_name: string (nullable = true)
    # |-- popularity: double (nullable = true)
    # |-- year: integer (nullable = true)
    # |-- genre: string (nullable = true)
    # |-- danceability: double (nullable = true)
    # |-- energy: double (nullable = true)
    # |-- key: integer (nullable = true)
    # |-- loudness: double (nullable = true)
    # |-- mode: integer (nullable = true)
    # |-- speechiness: double (nullable = true)
    # |-- acousticness: double (nullable = true)
    # |-- instrumentalness: double (nullable = true)
    # |-- liveness: double (nullable = true)
    # |-- valence: double (nullable = true)
    # |-- tempo: double (nullable = true)
    # |-- duration_ms: string (nullable = true)
    # |-- time_signature: string (nullable = true)
    # |-- year_2000-2004: integer (nullable = true)
    # |-- year_2005-2009: integer (nullable = true)
    # |-- year_2010-2014: integer (nullable = true)
    # |-- year_2015-2019: integer (nullable = true)
    # |-- year_2020-2024: integer (nullable = true)


def write_data_to_postgres(spark: SparkSession):

    def process_batch(df, epoch_id):
        jdbc_url = f"jdbc:postgresql://{secrets1.DB_HOST}:{secrets1.DB_PORT}/{secrets1.DB_NAME}"

        df.show()
        print(df.count())

        (df.write.format("jdbc")
            .mode("append")
            .option("url", jdbc_url)
            .option("driver", "org.postgresql.Driver")
            .option("dbtable", "tracks")
            .option("user", secrets1.DB_USER)
            .option("password", secrets1.DB_PASSWORD)
            .save())
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

    schema = StructType([
        StructField("track_id", StringType(), True),
        StructField("id", IntegerType(), True),
        StructField("artist_name", StringType(), True),
        StructField("track_name", StringType(), True),
        StructField("popularity", DoubleType(), True),
        StructField("year", IntegerType(), True),
        StructField("genre", StringType(), True),
        StructField("danceability", FloatType(), True), # change double->float
        StructField("energy", FloatType(), True),
        StructField("key", IntegerType(), True),
        StructField("loudness", DoubleType(), True),
        StructField("mode", IntegerType(), True),
        StructField("speechiness", FloatType(), True),
        StructField("acousticness", FloatType(), True),
        StructField("instrumentalness", FloatType(), True),
        StructField("liveness", FloatType(), True),
        StructField("valence", FloatType(), True),
        StructField("tempo", DoubleType(), True),
        StructField("duration_ms", IntegerType(), True),
        StructField("time_signature", IntegerType(), True),
        StructField("year_2000_2004", IntegerType(), True),
        StructField("year_2005_2009", IntegerType(), True),
        StructField("year_2010_2014", IntegerType(), True),
        StructField("year_2015_2019", IntegerType(), True),
        StructField("year_2020_2024", IntegerType(), True)
    ])

    (spark
        .readStream
        .option("maxFilesPerTrigger", 1)
        .schema(schema)
        .parquet("./data_ready_for_db_parquet2/")
        .writeStream
        .trigger(availableNow=True)
        .option("checkpointLocation", "./checkpointLocation/load_to_psg_2/")
        .foreachBatch(process_batch)
        # .outputMode("append")
        .start()
        .awaitTermination())


def try_sparkdf_to_pandasdf(spark: SparkSession):
    # Nested structure elements
    from pyspark.sql.types import StructType, StructField, StringType,IntegerType
    dataStruct = [(("James","","Smith"),"36636","M","3000"),
                  (("Michael","Rose",""),"40288","M","4000"),
                  (("Robert","","Williams"),"42114","M","4000"),
                  (("Maria","Anne","Jones"),"39192","F","4000"),
                  (("Jen","Mary","Brown"),"","F","-1")
                  ]

    schemaStruct = StructType([
        StructField('name', StructType([
            StructField('firstname', StringType(), True),
            StructField('middlename', StringType(), True),
            StructField('lastname', StringType(), True)
        ])),
        StructField('dob', StringType(), True),
        StructField('gender', StringType(), True),
        StructField('salary', StringType(), True)
    ])
    df = spark.createDataFrame(data=dataStruct, schema = schemaStruct)
    df.printSchema()

    pandasDF2 = df.toPandas()
    print(pandasDF2)


def try_feature_scaler(spark: SparkSession):
    from pyspark.sql import SparkSession
    from pyspark.sql import Row
    from pyspark.sql.functions import col
    from pyspark.ml.feature import MinMaxScaler, VectorAssembler
    from pyspark.ml.functions import vector_to_array
    from pyspark.ml.linalg import Vectors

    # Example feat_vec DataFrame with additional numerical columns
    data = [
        (10, -20, 100, 0.5, 3.2),
        (30, -10, 150, 0.7, 4.1),
        (60, -40, 200, 0.3, 2.9)
    ]

    columns = ['popularity', 'loudness', 'tempo', 'extra_feature1', 'extra_feature2']
    feat_vec = spark.createDataFrame(data, columns)

    # Define the columns to be scaled and the min/max values for those columns
    scale_columns = ['popularity', 'loudness', 'tempo']
    min_row = Row(popularity=0, loudness=-60, tempo=0, extra_feature1=0, extra_feature2=0)
    max_row = Row(popularity=100, loudness=0, tempo=250, extra_feature1=0, extra_feature2=0)

    # Convert min_row and max_row to DataFrames
    min_row_df = spark.createDataFrame([min_row])
    max_row_df = spark.createDataFrame([max_row])

    feat_vec = feat_vec.union(min_row_df).union(max_row_df)

    # Assemble all columns into a single feature vector
    assembler = VectorAssembler(inputCols=scale_columns, outputCol="features")
    feat_vec = assembler.transform(feat_vec)
    feat_vec.show()

    # Scale the features
    scaler = MinMaxScaler(inputCol="features", outputCol="scaled_features")
    scaler_model = scaler.fit(feat_vec)
    feat_vec = scaler_model.transform(feat_vec)

    feat_vec = feat_vec.filter(
        (col("popularity") != 0) & (col("popularity") != 100) &
        (col("loudness") != -60) & (col("loudness") != 0) &
        (col("tempo") != 0) & (col("tempo") != 250)
    )

    feat_vec.show()
    feat_vec.printSchema()

    # Extract the scaled features back into separate columns
    for i, col_name in enumerate(scale_columns):
        feat_vec = feat_vec.withColumn(col_name, vector_to_array(col("scaled_features")).getItem(i))

    # Show the final DataFrame with both scaled and non-scaled columns
    feat_vec.show()


def preprocess(spark: SparkSession):
    # get_track_id_counts(spark)
    # drop_duplicate_track_id_songs(spark)
    # process_data_write_csv_just_spark(spark)
    # validate_result(spark)
    # write_data_to_postgres(spark)
    pass


############### QUERY DB

import psycopg2
from IPython.display import display
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import glob


@contextmanager
def get_db(DATABASE_URL):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def query_db(query, return_early=False) -> pandas.DataFrame:
    DATABASE_URL="postgres://ghiabcwcxsyfvo:9de383d33fe38cec6d6bb1f41fa313df2f054cc6091bd08cb018f02e74c0cdd7@ec2-34-252-152-193.eu-west-1.compute.amazonaws.com:5432/d9mck4patkc46n"

    with get_db(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query)
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error: %s" % error)
                cur.close()
                return 1
            # The execute returns a list of tuples:
            tuples_list = cur.fetchall()
            cur.close()
            if return_early:
                return tuples_list

            columns = [
                "track_id",
                "id",
                "artist_name",
                "track_name",
                "popularity",
                "genre",
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
                "duration_ms",
                "time_signature",
                "year_2000_2004",
                "year_2005_2009",
                "year_2010_2014",
                "year_2015_2019",
                "year_2020_2024",
                "update_timestamp"
            ]

            # Now we need to transform the list into a pandas DataFrame:
            df = pd.DataFrame(tuples_list, columns=columns)
            display(df)
            return df


def weighted_mean(df, col="update_timestamp"):
    # print(df.dtypes)
    date_col = df[col]
    quantiles_values = date_col.quantile([0.25, 0.5, 0.75], interpolation="nearest")
    # print(quantiles_values)

    # calculate each quantile mean and multiply be matching weight
    # the later the records, the bigger the weight
    first_quantile_df = df[df[col] <= quantiles_values[0.25]].mean().drop(col).mul(1)
    second_quantile_df = df[(df[col] > quantiles_values[0.25]) & (df[col] <= quantiles_values[0.5])].mean().drop(col).mul(2)
    third_quantile_df = df[(df[col] > quantiles_values[0.5]) & (df[col] <= quantiles_values[0.75])].mean().drop(col).mul(3)
    fourth_quantile_df = df[df[col] > quantiles_values[0.75]].mean().drop(col).mul(4)

    # print("first")
    # display(first_quantile_df)
    # print("second")
    # display(second_quantile_df)
    # print("third")
    # display(third_quantile_df)
    # print("fourth")
    # display(fourth_quantile_df)

    all_quantile_df = pd.DataFrame({
        'first': first_quantile_df,
        'second': second_quantile_df,
        'third': third_quantile_df,
        'fourth': fourth_quantile_df})

    all_quantile_df = all_quantile_df.mean(axis=1)
    return all_quantile_df


from sklearn.metrics.pairwise import cosine_similarity
def get_recommandations(user_id=2):
    cols_for_similarity = [
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "loudness",
        "mode",
        "popularity",
        "speechiness",
        "tempo",
        "valence",
        "year_2000_2004",
        "year_2005_2009",
        "year_2010_2014",
        "year_2015_2019",
        "year_2020_2024",
        "update_timestamp"
    ]
    other_cols = ['artist_name', 'duration_ms', 'genre', 'id', 'key', 'time_signature', 'track_id', 'track_name']

    tracks_df = pd.concat(map(partial(pd.read_parquet),
                              glob.glob("data_ready_for_db_without_year_parquet/*.parquet")))
    tracks_similarity_df = tracks_df[cols_for_similarity[:-1]]
    tracks_other_cols_df = tracks_df[other_cols]
    display(tracks_df)

    user_likes_playlist = query_db(f"""
        select tracks.*, update_timestamp
        from likes
        join tracks on likes.track_id = tracks.track_id
        where user_id = {user_id}; """)

    user_likes_similarity_df = user_likes_playlist[cols_for_similarity]
    user_likes_other_cols_df = user_likes_playlist[other_cols]
    column_averages = weighted_mean(user_likes_similarity_df)
    user_likes_similarity_df_mean = pd.DataFrame([column_averages], index=['Average'])

    # display(user_likes_similarity_df_mean)

    tracks_similarity_df = tracks_similarity_df.sort_index(axis=1)
    user_likes_similarity_df_mean = user_likes_similarity_df_mean.sort_index(axis=1)

    similarity_scores = cosine_similarity(tracks_similarity_df, user_likes_similarity_df_mean)
    tracks_similarity_df['similarity_score'] = similarity_scores

    # TODO: join `tracks_other_cols_df` back
    # Reset indices to ensure uniqueness
    tracks_similarity_df = tracks_similarity_df.reset_index(drop=True)
    tracks_other_cols_df = tracks_other_cols_df.reset_index(drop=True)
    display(tracks_similarity_df)
    display(tracks_other_cols_df)
    scored_tracks_df = pd.concat([tracks_similarity_df, tracks_other_cols_df], axis=1, join='inner')

    top_similarities = scored_tracks_df.sort_values(by='similarity_score', ascending=False)
    top_similarities = top_similarities[['track_id', 'track_name', 'artist_name', 'similarity_score']]
    print("top_similarities")
    display(top_similarities)

######################################


from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_KEY="248cf0f2-be45-4f5e-9854-67884f601c89"


@contextmanager
def get_pinecone_conn(index_name: str):
    # Initialize Pinecone connection
    pc = Pinecone(api_key=PINECONE_API_KEY)
    conn = pc.Index(index_name)
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        # Explicitly delete the connection object
        del conn


def get_tracks_df(user_id: int, type: str):
    tuples_list = []
    if type == "like":
        tuples_list = query_db(f"""
            SELECT tracks.*, update_timestamp
            FROM likes
            JOIN tracks ON likes.track_id = tracks.track_id
            WHERE likes.user_id = {user_id};
            """)
    else:
        tuples_list = query_db(f"""
            SELECT tracks.*, update_timestamp
            FROM dislikes
            JOIN tracks ON dislikes.track_id = tracks.track_id
            WHERE dislikes.user_id = {user_id};
            """)

    columns = [
        "track_id",
        "id",
        "artist_name",
        "track_name",
        "popularity",
        "year",
        "genre",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "time_signature",
        "year_2000_2004",
        "year_2005_2009",
        "year_2010_2014",
        "year_2015_2019",
        "year_2020_2024",
        "update_timestamp"
    ]

    # transform the list into a pandas DataFrame
    df = pd.DataFrame(tuples_list, columns=columns)
    # display(df)
    return df


def get_tracks_by_track_id_score(top_tracks):
    """
    SELECT track_id, track_name, artist_name, relevance_percentage, year
    FROM tracks
    JOIN (  SELECT track_id_col, relevance_percentage
            FROM (
                VALUES ('3IfBNSetM8bgPObhggD3Yq', 0.99),
                       ('1MYaHGczevRznjDOf90Gfp', 0.88)
            ) AS derived_table(track_id_col, relevance_percentage)) as recommended
    ON tracks.track_id = recommended.track_id_col;
    """
    values_clause = ", ".join([f"('{track_id}', {relevance_percentage})" for track_id, relevance_percentage in top_tracks])
    query = f"""
        SELECT track_id, track_name, artist_name, relevance_percentage, year
        FROM tracks
        JOIN (
            SELECT track_id_col, relevance_percentage
            FROM (
                VALUES {values_clause}
            ) AS derived_table(track_id_col, relevance_percentage)
        ) AS recommended
        ON tracks.track_id = recommended.track_id_col;"""
    print(query)

    result = query_db(query, return_early=True)
    print(result)
    return result


def get_likes_by_user_id_score(top_users, user_id):
    """
    WITH
    current_user_likes_dislikes AS (
        SELECT likes.track_id, likes.user_id
        FROM likes
        WHERE user_id = 34
        UNION
        SELECT dislikes.track_id, dislikes.user_id
        FROM dislikes
        WHERE user_id = 34
    )
    SELECT tracks.track_id, track_name, artist_name, top_users.relevance_percentage, year
    FROM (  SELECT user_id_col, relevance_percentage
            FROM (
                VALUES (CAST('34' AS INT), 0.99),
                       (CAST('35' AS INT), 0.88)
            ) AS derived_table(user_id_col, relevance_percentage)) as top_users
    JOIN likes ON top_users.user_id_col = likes.user_id
    JOIN tracks ON likes.track_id = tracks.track_id
    LEFT OUTER JOIN current_user_likes_dislikes ON tracks.track_id = current_user_likes_dislikes.track_id
    WHERE current_user_likes_dislikes.track_id IS NULL;
    """

    values_clause = ", ".join([f"(CAST('{track_id}' AS INT), {relevance_percentage})" for track_id, relevance_percentage in top_users])
    query = f"""
        WITH
        current_user_likes_dislikes AS (
            SELECT likes.track_id, likes.user_id
            FROM likes
            WHERE user_id = {user_id}
            UNION
            SELECT dislikes.track_id, dislikes.user_id
            FROM dislikes
            WHERE user_id = {user_id}
        )
        SELECT tracks.track_id, track_name, artist_name, top_users.relevance_percentage, year
        FROM (  SELECT user_id_col, relevance_percentage
                FROM (
                VALUES {values_clause}
                    ) AS derived_table(user_id_col, relevance_percentage)) as top_users
        JOIN likes ON top_users.user_id_col = likes.user_id
        JOIN tracks ON likes.track_id = tracks.track_id
        LEFT OUTER JOIN current_user_likes_dislikes ON tracks.track_id = current_user_likes_dislikes.track_id
        WHERE current_user_likes_dislikes.track_id IS NULL;
        """
    print(query)

    result = query_db(query, return_early=True)
    print(result)
    return result


def get_recommendations__listening_history(user_id=7):

    cols_for_similarity = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "mode",
                       "popularity", "speechiness", "tempo", "valence",
                       "year_2000_2004", "year_2005_2009", "year_2010_2014", "year_2015_2019", "year_2020_2024",
                       "update_timestamp"]
    other_cols = ['artist_name', 'duration_ms', 'genre', 'id', 'key', 'year', 'time_signature', 'track_id', 'track_name']

    user_likes_playlist = get_tracks_df(user_id, type="like")
    user_dislikes_playlist = get_tracks_df(user_id, type="dislike")

    if len(user_likes_playlist) == 0:
        return []

    user_likes_similarity_df = user_likes_playlist[cols_for_similarity]
    user_likes_other_cols_df = user_likes_playlist[other_cols]
    # display(user_likes_similarity_df)

    column_averages = weighted_mean(user_likes_similarity_df).tolist()
    # user_likes_similarity_df_mean = pd.DataFrame([column_averages], index=['Average'])
    # display(column_averages)

    top_ids_scores = []
    with get_pinecone_conn() as conn:
        # Query Pinecone 'tracks' index, using 'cosine' metric, to find the top most similar vectors
        query_result = conn.query(vector=column_averages, top_k=70)
        top_ids_scores = [(match['id'], match['score']) for match in query_result['matches']]
        # print(top_ids)
        print(top_ids_scores)

    # Delete already liked, and disliked tracks
    likes_track_ids = user_likes_playlist['track_id'].tolist()
    dislikes_track_ids = user_dislikes_playlist['track_id'].tolist()

    top_ids_scores = [(t_id, t_score)
                      for t_id, t_score in top_ids_scores
                      if t_id not in likes_track_ids and t_id not in dislikes_track_ids]
    print(top_ids_scores)

    if len(top_ids_scores) > 0:
        result = get_tracks_by_track_id_score(top_ids_scores)


def get_recommendations_by_similar_users(user_id=32):
    pass
    # get user like and dislikes
    user_likes_playlist = get_tracks_df(user_id, type="like")
    user_dislikes_playlist = get_tracks_df(user_id, type="dislike")
    # if len(user_likes_playlist) == 0:
    #     return []

    top_ids_scores = []
    with get_pinecone_conn('users') as users_index:
        # get user vector from pinecone
        retrieve_user_results = users_index.fetch(ids=[str(user_id)])
        user_record = retrieve_user_results.get('vectors').get(str(user_id))

        if not user_record:
            return []
        user_vector = user_record['values']
        print(f"user_vector: {user_vector}")

        # get similar user from pinecone, take top k user_id
        # Query Pinecone 'users' index, using 'cosine' metric, to find the top most similar vectors
        query_user_results = users_index.query(vector=user_vector, top_k=20)
        top_ids_scores = [(match['id'], match['score']) for match in query_user_results['matches']]
        print(f"top_ids_scores: {top_ids_scores}")

    if not len(top_ids_scores):
        return []

    result = get_likes_by_user_id_score(top_ids_scores, user_id)
    print(len(result))
    return result
    # get user liked tracks - how? TBD
    # filter out like and dislikes of current user

if __name__ == "__main__":
    # spark = config_spark()
    print("hello")
    # preprocess(spark)
    # get_recommendations_pinecone()
    get_recommendations_by_similar_users()
    print("end")
    # get_recommandations()



