from pyspark.sql import SparkSession

from pyspark.config import SparkConfig


# Builds a local SparkSession wired to a filesystem-backed Iceberg Hadoop catalog
def get_spark_session():
    catalog = SparkConfig.CATALOG_NAME
    SparkConfig.WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)

    return (
        SparkSession.builder.appName(SparkConfig.APP_NAME)
        .master("local[*]")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(f"spark.sql.catalog.{catalog}", "org.apache.iceberg.spark.SparkCatalog")
        .config(f"spark.sql.catalog.{catalog}.type", "hadoop")
        .config(f"spark.sql.catalog.{catalog}.warehouse", str(SparkConfig.WAREHOUSE_DIR))
        .getOrCreate()
    )
