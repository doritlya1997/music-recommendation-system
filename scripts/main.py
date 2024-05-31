from delta import configure_spark_with_delta_pip
from tempfile import TemporaryDirectory
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import functions as F
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

if __name__ == "__main__":
    # spark = config_spark()
    print("hello")
    # preprocess(spark)
    print("end")



