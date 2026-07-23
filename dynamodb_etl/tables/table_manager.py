from dynamodb_etl.tables.schemas import TABLE_SCHEMAS


# Creates tables if missing, does not migrate existing ones
class TableManager:
    @staticmethod
    def create_tables_if_not_exist(client) -> None:
        existing = {t.name for t in client.tables.all()}

        for table_name, schema in TABLE_SCHEMAS.items():
            if table_name in existing:
                print(f"Already exists: {table_name}")
                continue

            client.create_table(
                TableName=table_name,
                KeySchema=schema["key_schema"],
                AttributeDefinitions=schema["attribute_definitions"],
                BillingMode="PAY_PER_REQUEST",
            )
            print(f"Created table: {table_name}")

        for table_name in TABLE_SCHEMAS:
            client.Table(table_name).wait_until_exists()
