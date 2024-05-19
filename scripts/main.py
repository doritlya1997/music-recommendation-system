from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
from tempfile import TemporaryDirectory
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.types import *
from pyspark.sql.functions import *
from pyspark.sql import window
from pyspark.sql import functions as F

def main():
    tmpdir = TemporaryDirectory()
    builder = (
        SparkSession.builder.master("local[*]")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", f"file:///{tmpdir.name}")
    )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()


if __name__ == "__main__":
    main()