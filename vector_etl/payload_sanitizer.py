from datetime import date, datetime
from decimal import Decimal

# Converts Decimal/datetime/GIS Point values from Django ORM into JSON-safe types
class PayloadSanitizer:
    @classmethod
    def sanitize(cls, value):
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if hasattr(value, "x") and hasattr(value, "y"):
            return {"lat": value.y, "lon": value.x}
        if isinstance(value, dict):
            return {k: cls.sanitize(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls.sanitize(v) for v in value]
        return value

    @classmethod
    def sanitize_row(cls, row: dict) -> dict:
        return {k: cls.sanitize(v) for k, v in row.items()}