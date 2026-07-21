import glob

from pyspark.sql import SparkSession

from pyspark_etl.config import SparkConfig

SPARK_JARS_DIR = "/opt/spark-jars"


# Builds a local SparkSession wired to a filesystem-backed Iceberg Hadoop catalog
def get_spark_session():
    catalog = SparkConfig.CATALOG_NAME
    SparkConfig.WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    jars = ",".join(sorted(glob.glob(f"{SPARK_JARS_DIR}/*.jar")))

    return (
        SparkSession.builder.appName(SparkConfig.APP_NAME)
        .master("local[*]")
        .config("spark.jars", jars)
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog}.type", "hadoop")
        .config(f"spark.sql.catalog.{catalog}.warehouse", str(SparkConfig.WAREHOUSE_DIR))
        .getOrCreate()
    )