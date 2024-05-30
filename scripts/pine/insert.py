# from backend.app.database import get_pinecone_conn
from contextlib import contextmanager

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
from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = "248cf0f2-be45-4f5e-9854-67884f601c89"


@contextmanager
def get_pinecone_conn():
    # Initialize Pinecone connection
    pc = Pinecone(api_key=PINECONE_API_KEY)
    conn = pc.Index('tracks')
    try:
        yield conn
    except Exception as e:
        print(e)
    finally:
        # Explicitly delete the connection object
        del conn


def config_spark():
    tmpdir = TemporaryDirectory()
    builder = (
        SparkSession.builder.master("local[*]")
        .config("spark.jars", "./jar/postgresql-42.7.3.jar")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", f"file:///{tmpdir.name}")
        .config("spark.executor.memory", "4g")  # Increase executor memory
        .config("spark.driver.memory", "4g")  # Increase driver memory
    )

    return configure_spark_with_delta_pip(builder).getOrCreate()


schema = StructType([
    StructField("track_id", StringType(), True),
    StructField("id", IntegerType(), True),
    StructField("artist_name", StringType(), True),
    StructField("track_name", StringType(), True),
    StructField("popularity", DoubleType(), True),
    StructField("year", IntegerType(), True),
    StructField("genre", StringType(), True),
    StructField("danceability", FloatType(), True),  # change double->float
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


def insert_to_index(spark: SparkSession, conn):
    def process_batch(df, epoch_id):
        feat_vec = df.select(
            "track_id",
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
            "year_2020_2024"
        ).collect()

        vectors = [
            {
                "id": row["track_id"],
                "values": [
                    float(row["acousticness"]),
                    float(row["danceability"]),
                    float(row["energy"]),
                    float(row["instrumentalness"]),
                    float(row["liveness"]),
                    float(row["loudness"]),
                    float(row["mode"]),
                    float(row["popularity"]),
                    float(row["speechiness"]),
                    float(row["tempo"]),
                    float(row["valence"]),
                    float(row["year_2000_2004"]),
                    float(row["year_2005_2009"]),
                    float(row["year_2010_2014"]),
                    float(row["year_2015_2019"]),
                    float(row["year_2020_2024"])
                ]
            }
            for row in feat_vec
        ]

        # Define the number of iterations
        num_iterations = 1000

        # Calculate the quarter size
        quarter_size = len(vectors) // num_iterations

        # Iterate over the quarters of the array
        for i in range(num_iterations):
            start_index = i * quarter_size
            end_index = (i + 1) * quarter_size
            quarter = vectors[start_index:end_index]
            print(f"{len(quarter)}")
            conn.upsert(vectors=quarter)



    spark.readStream \
        .schema(schema) \
        .parquet('../data_ready_for_db_parquet') \
        .writeStream \
        .foreachBatch(process_batch) \
        .trigger(availableNow=True) \
        .option("checkpointLocation", "./checkpointLocation/insertPicone1") \
        .option("maxFilesPerTrigger", 1) \
        .start() \
        .awaitTermination()


if __name__ == "__main__":
    spark = config_spark()
    with get_pinecone_conn() as conn:
        insert_to_index(spark, conn)
