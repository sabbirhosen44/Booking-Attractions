from decimal import Decimal

from dynamodb_etl.tables.schema_aligner import SchemaAligner


# Converts floats to Decimal, required by boto3's dynamodb resource
class DecimalConverter:
    @classmethod
    def convert(cls, value):
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, dict):
            return {k: cls.convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [cls.convert(v) for v in value]
        return value


# Batch writes items into a table, uses boto3's built-in 25-item batching
class DynamoWriteService:
    def __init__(self, client):
        self.client = client

    def batch_write(self, table_name: str, items: list, key_fields: list | None = None) -> None:
        if not items:
            return

        if key_fields:
            deduped = {}
            for item in items:
                key = tuple(item.get(f) for f in key_fields)
                deduped[key] = item
            items = list(deduped.values())

        items = SchemaAligner.align_all(table_name, items)

        table = self.client.Table(table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=DecimalConverter.convert(item))