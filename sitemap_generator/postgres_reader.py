from django.db import connection


from apps.attractions.models import RentalProperty

class SitemapPostgresReader:
    @staticmethod
    def iter_property_batches(batch_size: int):
        queryset = (
            RentalProperty.objects
            .values(
                "id",
                "property_slug",
                "images",
                "updated_at",
            )
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
    def iter_nearby_property_batches(batch_size: int):
        sql = """
            SELECT DISTINCT
                p2.id,
                p2.property_slug,
                p2.images,
                p2.updated_at
            FROM attractions_rentalproperty p1
            JOIN attractions_rentalproperty p2
                ON ST_DWithin(
                    p1.geography_latlon,
                    p2.geography_latlon,
                    5000
                )
            WHERE
                p1.id <> p2.id
                AND p1.geography_latlon IS NOT NULL
                AND p2.geography_latlon IS NOT NULL
            ORDER BY p2.id;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql)

            columns = [col[0] for col in cursor.description]

            while True:
                rows = cursor.fetchmany(batch_size)

                if not rows:
                    break

                yield [
                    dict(zip(columns, row))
                    for row in rows
                ]