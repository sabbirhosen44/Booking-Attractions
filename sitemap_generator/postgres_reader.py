from django.db import connection

from apps.attractions.models import RentalProperty


class SitemapPostgresReader:
    @staticmethod
    def iter_property_batches(batch_size: int):
        queryset = (
            RentalProperty.objects
            .values("id", "property_slug", "images", "updated_at")
            .order_by("id")
            .iterator(chunk_size=batch_size)
        )

        batch = []
        for row in queryset:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch

    @staticmethod
    def iter_nearby_property_batches(batch_size: int, radius_km: float):
        radius_meters = radius_km * 1000

        sql = """
            SELECT DISTINCT
                p2.id,
                p2.property_slug,
                p2.images,
                p2.updated_at
            FROM rental_property p1
            JOIN rental_property p2
                ON ST_DWithin(p1.geography_latlon, p2.geography_latlon, %s)
            WHERE
                p1.id <> p2.id
                AND p1.geography_latlon IS NOT NULL
                AND p2.geography_latlon IS NOT NULL
            ORDER BY p2.id;
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [radius_meters])
                columns = [col[0] for col in cursor.description]

                while True:
                    rows = cursor.fetchmany(batch_size)
                    if not rows:
                        break
                    yield [dict(zip(columns, row)) for row in rows]
        except OperationalError as e:
            print(f"Could not connect to database : {e}")
            raise