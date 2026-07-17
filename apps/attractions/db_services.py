from apps.attractions.models import (
    Feed,
    PriceHistory,
    PropertyImageMeta,
    PropertyReviews,
    RentalProperty,
    RentalPropertyLocalize,
    SkipProperties,
)

from core.utils.partition_manager import PartitionManager

RENTAL_PROPERTY_FIELDS = [
    "booking_id",
    "feed",
    "property_name",
    "property_slug",
    "property_type",
    "activity_categories",
    "property_attributes",
    "review_score_general",
    "review_score",
    "number_of_review",
    "languages",
    "supported_languages",
    "images",
    "uploaded_image_count",
    "feed_provider_url",
    "partners_url",
    "display",
    "zip_code",
    "country_code",
    "country",
    "city",
    "location_id",
    "latlon",
    "geography_latlon",
]

RENTAL_PROPERTY_LOCALIZE_FIELDS = [
    "feed",
    "property_name",
    "property_description",
    "property_slug",
    "property_type",
    "address",
]

PROPERTY_REVIEWS_FIELDS = [
    "feed",
    "country_code",
    "language_code",
    "score",
    "summary",
    "reviewer",
    "review_date",
]


# Handles saving attraction details, translations, photos and price/date updates in the database
class AttractionDBService:

    @staticmethod
    def save_properties(rows):
        if not rows:
            return

        unique_rows = {row["id"]: row for row in rows}
        instances = [RentalProperty(**row) for row in unique_rows.values()]

        RentalProperty.objects.bulk_create(
            instances,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=RENTAL_PROPERTY_FIELDS,
        )

    @staticmethod
    def save_localized(rows):
        if not rows:
            return

        unique_rows = {}
        for row in rows:
            key = (row["property_id"], row["language"], row.get("country_code"))
            unique_rows[key] = row

        rows_to_insert = list(unique_rows.values())
        for row in rows_to_insert:
            PartitionManager.ensure_partition(RentalPropertyLocalize, row.get("country_code"))

        instances = [RentalPropertyLocalize(**row) for row in rows_to_insert]

        RentalPropertyLocalize.objects.bulk_create(
            instances,
            update_conflicts=True,
            unique_fields=["property_id", "language", "country_code"],
            update_fields=RENTAL_PROPERTY_LOCALIZE_FIELDS,
        )

    @staticmethod
    def save_photos(rows):
        if not rows:
            return

        unique_rows = {}
        for row in rows:
            key = (row["property_id"], row["url"])
            unique_rows[key] = row

        rows_to_insert = list(unique_rows.values())
        for row in rows_to_insert:
            PartitionManager.ensure_partition(PropertyImageMeta, row.get("country_code"))

        instances = [PropertyImageMeta(**row) for row in rows_to_insert]

        PropertyImageMeta.objects.bulk_create(
            instances,
            ignore_conflicts=True,
        )

    @staticmethod
    def get_existing_attraction_ids():
        return set(
            RentalProperty.objects.filter(
                feed=int(Feed.BOOKING_ATTRACTION)
            ).values_list("id", flat=True)
        )

    @staticmethod
    def get_existing_attraction_country_map():
        return dict(
            RentalProperty.objects.filter(
                feed=int(Feed.BOOKING_ATTRACTION)
            ).values_list("id", "country_code")
        )

    @staticmethod
    def update_pricing(updates):
        if not updates:
            return

        properties = RentalProperty.objects.filter(id__in=updates.keys())
        to_update = []

        for prop in properties:
            currency, total = updates[prop.id]
            prop.currency = currency
            prop.usd_price = total
            to_update.append(prop)

        if to_update:
            RentalProperty.objects.bulk_update(to_update, ["currency", "usd_price"])

    @staticmethod
    def update_dates(updates):
        if not updates:
            return

        properties = RentalProperty.objects.filter(id__in=updates.keys())
        to_update = []

        for prop in properties:
            check_in, check_out = updates[prop.id]
            prop.check_in = check_in.isoformat() if check_in else None
            prop.check_out = check_out.isoformat() if check_out else None
            to_update.append(prop)

        if to_update:
            RentalProperty.objects.bulk_update(to_update, ["check_in", "check_out"])


# Handles saving attraction reviews in the database
class ReviewDBService:

    @staticmethod
    def save_reviews(rows):
        if not rows:
            return

        unique_rows = {}
        for row in rows:
            key = (row["id"], row.get("country_code"))
            unique_rows[key] = row

        rows_to_insert = list(unique_rows.values())
        for row in rows_to_insert:
            PartitionManager.ensure_partition(PropertyReviews, row.get("country_code"))

        instances = [PropertyReviews(**row) for row in rows_to_insert]

        PropertyReviews.objects.bulk_create(
            instances,
            update_conflicts=True,
            unique_fields=["id", "country_code"],
            update_fields=PROPERTY_REVIEWS_FIELDS,
        )


# Handles saving attraction review scores in the database
class ReviewScoreDBService:

    @staticmethod
    def save_scores(scores_by_attraction):
        if not scores_by_attraction:
            return

        properties = RentalProperty.objects.filter(id__in=scores_by_attraction.keys())
        to_update = []

        for prop in properties:
            prop.review_scores = scores_by_attraction[prop.id]
            to_update.append(prop)

        if to_update:
            RentalProperty.objects.bulk_update(to_update, ["review_scores"])


# Handles saving attractions that were skipped during import
class SkipPropertiesDBService:

    @staticmethod
    def save_skips(rows):
        if not rows:
            return

        unique_rows = {row["property_id"]: row for row in rows}
        instances = [
            SkipProperties(
                property_id=row["property_id"],
                feed=Feed.BOOKING_ATTRACTION,
                reason=row["reason"],
                updated_by="import_attractions",
            )
            for row in unique_rows.values()
        ]

        SkipProperties.objects.bulk_create(
            instances,
            update_conflicts=True,
            unique_fields=["property_id"],
            update_fields=["feed", "reason", "updated_by", "updated_at"],
        )


# Handles saving attraction price history in the database
class PriceHistoryDBService:

    @staticmethod
    def save_prices(rows):
        if not rows:
            return

        for row in rows:
            PartitionManager.ensure_partition(PriceHistory, row.get("country_code"))

        instances = [PriceHistory(**row) for row in rows]

        PriceHistory.objects.bulk_create(instances)