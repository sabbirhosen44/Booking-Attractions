import uuid


# Low-level Iceberg write operations: upsert, append, update
class IcebergWriter:

    @staticmethod
    def upsert(spark, df, table, merge_keys):
        if df.rdd.isEmpty():
            return

        view = f"src_{uuid.uuid4().hex}"
        df.createOrReplaceTempView(view)

        cols = df.columns
        on_clause = " AND ".join(f"t.{k} = s.{k}" for k in merge_keys)
        update_set = ", ".join(f"t.{c} = s.{c}" for c in cols if c not in merge_keys)
        insert_cols = ", ".join(cols)
        insert_vals = ", ".join(f"s.{c}" for c in cols)

        spark.sql(f"""
            MERGE INTO {table} t
            USING {view} s
            ON {on_clause}
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """)

        spark.catalog.dropTempView(view)

    @staticmethod
    def append(df, table):
        if df.rdd.isEmpty():
            return

        df.writeTo(table).append()

    @staticmethod
    def update_columns(spark, updates_df, table, key, update_cols):
        if updates_df.rdd.isEmpty():
            return

        view = f"src_{uuid.uuid4().hex}"
        updates_df.createOrReplaceTempView(view)

        set_clause = ", ".join(f"t.{c} = s.{c}" for c in update_cols)

        spark.sql(f"""
            MERGE INTO {table} t
            USING {view} s
            ON t.{key} = s.{key}
            WHEN MATCHED THEN UPDATE SET {set_clause}
        """)

        spark.catalog.dropTempView(view)
