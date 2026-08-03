from django.contrib.gis.measure import D

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
        seen = set()
        batch = []

        queryset = (
            RentalProperty.objects
            .exclude(geography_latlon__isnull=True)
            .values(
                "id",
                "property_slug",
                "images",
                "updated_at",
                "geography_latlon",
            )
            .order_by("id")
            .iterator(chunk_size=batch_size)
        )

        for property_row in queryset:
            nearby_queryset = (
                RentalProperty.objects
                .exclude(id=property_row["id"])
                .exclude(geography_latlon__isnull=True)
                .filter(
                    geography_latlon__distance_lte=(
                        property_row["geography_latlon"],
                        D(km=5),
                    )
                )
                .values(
                    "id",
                    "property_slug",
                    "images",
                    "updated_at",
                )
            )

            for nearby in nearby_queryset:
                property_id = nearby["id"]

                if property_id in seen:
                    continue

                seen.add(property_id)

                batch.append(nearby)

                if len(batch) >= batch_size:
                    yield batch
                    batch = []

        if batch:
            yield batch