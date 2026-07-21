from pyspark.sql import functions as F

from pyspark_etl.catalog.schema_defs import TABLE_COLUMNS


# Adds every column from the table's full schema that isn't already present in df as a typed NULL, and returns the columns in schema order
def align_to_schema(df, table_name):
    columns = TABLE_COLUMNS[table_name]
    existing = set(df.columns)

    for name, dtype in columns:
        if name not in existing:
            df = df.withColumn(name, F.lit(None).cast(dtype.lower()))

    return df.select(*[name for name, _ in columns])
