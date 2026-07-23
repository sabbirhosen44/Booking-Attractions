from dynamodb_etl.tables.schema_fields import TABLE_FIELDS

# Sort keys that exist only in DynamoDB, not in the Postgres model,
# needed because those tables have no real unique key to use instead.
EXTRA_KEY_FIELDS = {
    "rental_property_localize": ["language_country_code"],
}


# Pads every item to the table's full field set with None for gaps
class SchemaAligner:
    @staticmethod
    def align(table_name: str, item: dict) -> dict:
        fields = TABLE_FIELDS[table_name]
        aligned = {field: item.get(field) for field in fields}

        for extra_field in EXTRA_KEY_FIELDS.get(table_name, []):
            aligned[extra_field] = item.get(extra_field)

        return aligned

    @classmethod
    def align_all(cls, table_name: str, items: list) -> list:
        return [cls.align(table_name, item) for item in items]