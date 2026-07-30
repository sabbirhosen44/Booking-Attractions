from apps.attractions.models import RentalProperty


# Reads rental_property data needed for sitemap generation
class SitemapPostgresReader:
    @staticmethod
    def iter_property_batches(batch_size: int):
        queryset = RentalProperty.objects.values(
            "id", "property_slug", "images", "updated_at"
        ).order_by("id").iterator(chunk_size=batch_size)

        batch = []
        for row in queryset:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    @staticmethod
    def city_groups() -> list:
        pairs = (
            RentalProperty.objects
            .exclude(city__isnull=True)
            .exclude(city__exact="")
            .values("country_code", "city")
            .distinct()
        )

        groups = []
        for pair in pairs:
            sample = (
                RentalProperty.objects
                .filter(country_code=pair["country_code"], city=pair["city"])
                .exclude(images__len=0)
                .values_list("images", flat=True)
                .first()
            )
            groups.append({
                "country_code": pair["country_code"],
                "city": pair["city"],
                "sample_image": sample[0] if sample else None,
            })
        return groups
