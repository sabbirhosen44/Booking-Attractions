from apps.attractions.models import RentalProperty


class PostgresPropertyReader:

    FIELDS = (
        "booking_id",
        "property_name",
        "property_slug",
        "city",
        "country_code",
        "property_type",
        "usd_price",
    )

    def read(self):
        queryset = (
            RentalProperty.objects
            .values(*self.FIELDS)
            .order_by("id")
        )

        for property_data in queryset.iterator(chunk_size=5000):
            yield property_data