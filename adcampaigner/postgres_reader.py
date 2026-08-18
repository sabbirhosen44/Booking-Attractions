from apps.attractions.models import RentalProperty


class PostgresPropertyReader:

    FIELDS = (
    "booking_id",
    "property_name",
    "property_slug",
    "city",
    "state",
    "country_code",
    "property_type",
    "activity_categories",
    "property_attributes",
    "images",
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