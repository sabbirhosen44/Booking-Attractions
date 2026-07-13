import threading

from django.db import connection



class PartitionManager:

    _ensured = set()
    _lock = threading.Lock()

    @classmethod
    def ensure_partition(cls, model, country_code):
        country_code = (country_code or "xx").lower()
        table = model._meta.db_table
        key = (table, country_code)

        if key in cls._ensured:
            return

        with cls._lock:
            if key in cls._ensured:
                return

            partition_name = f"{table}_{country_code}"

            with connection.cursor() as cursor:
                cursor.execute(
                    f'CREATE TABLE IF NOT EXISTS "{partition_name}" '
                    f'PARTITION OF "{table}" FOR VALUES IN (%s)',
                    [country_code],
                )

            cls._ensured.add(key)
