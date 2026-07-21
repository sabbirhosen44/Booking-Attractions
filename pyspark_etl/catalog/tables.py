from pyspark_etl.catalog.schema_defs import PARTITIONED_TABLES, TABLE_COLUMNS
from pyspark_etl.config import SparkConfig


def _ddl_for(table_name, columns):
    column_lines = ",\n            ".join(f"{name} {dtype}" for name, dtype in columns)
    partition_clause = (
        "\n        PARTITIONED BY (country_code)" if table_name in PARTITIONED_TABLES else ""
    )

    return f"""
        CREATE TABLE IF NOT EXISTS {{table}} (
            {column_lines}
        ) USING iceberg{partition_clause}
    """

# Creates the Iceberg database and every target table with its full, model-matching column set
def ensure_tables(spark):
    catalog = SparkConfig.CATALOG_NAME
    db = SparkConfig.DATABASE

    spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog}.{db}")

    for table_name, columns in TABLE_COLUMNS.items():
        ddl = _ddl_for(table_name, columns).format(table=SparkConfig.table(table_name))
        spark.sql(ddl)
