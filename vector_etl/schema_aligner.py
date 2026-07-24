from vector_etl.schema_fields import RENTAL_PROPERTY_FIELDS


# Pads every payload to the full 119 rental_property fields, None for gaps
class SchemaAligner:
    @staticmethod
    def align(payload: dict) -> dict:
        return {field: payload.get(field) for field in RENTAL_PROPERTY_FIELDS}