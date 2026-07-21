from pyspark.sql import functions as F

from pyspark_etl.catalog.schema_defs import TableSchemas


# Pads a DataFrame to a table's full column set
class SchemaAligner:

    @staticmethod
    def align(df, table_name):
        columns = TableSchemas.columns_for(table_name)
        existing = set(df.columns)

        for name, dtype in columns:
            if name not in existing:
                df = df.withColumn(name, F.lit(None).cast(dtype.lower()))

        return df.select(*[name for name, _ in columns])
