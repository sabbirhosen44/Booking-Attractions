import glob

from pyspark.sql import SparkSession

from pyspark_etl.config import SparkConfig

SPARK_JARS_DIR = "/opt/spark-jars"


# Builds the local SparkSession with Iceberg catalog
class SparkSessionFactory:

    @staticmethod
    def create():
        catalog = SparkConfig.CATALOG_NAME
        SparkConfig.WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

        jars = ",".join(sorted(glob.glob(f"{SPARK_JARS_DIR}/*.jar")))

        return (
            SparkSession.builder.appName(SparkConfig.APP_NAME)
            .master("local[2]")
            .config("spark.jars", jars)
            .config("spark.driver.memory", "2g")
            .config("spark.sql.codegen.wholeStage", "false")
            .config(
                "spark.sql.extensions",
                "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
            )
            .config(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
            .config(f"spark.sql.catalog.{catalog}.type", "hadoop")
            .config(f"spark.sql.catalog.{catalog}.warehouse", str(SparkConfig.WAREHOUSE_DIR))
            .getOrCreate()
        )