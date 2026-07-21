from pyspark_etl.catalog.schema_defs import TableSchemas
from pyspark_etl.config import SparkConfig


# Creates the Iceberg database and target tables
class IcebergTableManager:

    @staticmethod
    def _ddl_for(table_name, columns):
        column_lines = ",\n            ".join(f"{name} {dtype}" for name, dtype in columns)
        partition_clause = (
            "\n        PARTITIONED BY (country_code)"
            if TableSchemas.is_partitioned(table_name)
            else ""
        )

        return f"""
        CREATE TABLE IF NOT EXISTS {{table}} (
            {column_lines}
        ) USING iceberg{partition_clause}
    """

    @classmethod
    def ensure_tables(cls, spark):
        catalog = SparkConfig.CATALOG_NAME
        db = SparkConfig.DATABASE

        spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog}.{db}")

        for table_name in TableSchemas.TABLE_COLUMNS:
            columns = TableSchemas.columns_for(table_name)
            ddl = cls._ddl_for(table_name, columns).format(table=SparkConfig.table(table_name))
            spark.sql(ddl)
