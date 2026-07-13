from psqlextra.types import ConflictAction

from apps.attractions.models import (
    Feed,
    PriceHistory,
    PropertyImageMeta,
    PropertyReviews,
    RentalProperty,
    RentalPropertyLocalize,
)

from core.utils.partition_manager import PartitionManager


# Handles all database operations related to RentalProperty rows built from attraction_details, plus their localized content and photos.
class AttractionDBService:

    @staticmethod
    def save_properties(rows):
        if not rows:
            return

        unique_rows = {row["id"]: row for row in rows}

        RentalProperty.objects.on_conflict(
            ["id"],
            ConflictAction.UPDATE,
        ).bulk_insert(list(unique_rows.values()))

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
            PartitionManager.ensure_partition(
                RentalPropertyLocalize, row.get("country_code")
            )

        RentalPropertyLocalize.objects.on_conflict(
            ["property_id", "language", "country_code"],
            ConflictAction.UPDATE,
        ).bulk_insert(rows_to_insert)

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
            PartitionManager.ensure_partition(
                PropertyImageMeta, row.get("country_code")
            )

        PropertyImageMeta.objects.on_conflict(
            ["property_id", "path", "country_code"],
            ConflictAction.NOTHING,
        ).bulk_insert(rows_to_insert)

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
            RentalProperty.objects.bulk_update(
                to_update, ["currency", "usd_price"]
            )


# Handles all database operations related to attraction reviews.
class ReviewDBService:

    @staticmethod
    def save_reviews(rows):
        if not rows:
            return

        unique_rows = {row["id"]: row for row in rows}
        rows_to_insert = list(unique_rows.values())

        for row in rows_to_insert:
            PartitionManager.ensure_partition(
                PropertyReviews, row.get("country_code")
            )

        PropertyReviews.objects.on_conflict(
            ["id"],
            ConflictAction.UPDATE,
        ).bulk_insert(rows_to_insert)


# Handles review score breakdowns.
class ReviewScoreDBService:

    @staticmethod
    def save_scores(scores_by_attraction):
        if not scores_by_attraction:
            return

        properties = RentalProperty.objects.filter(
            id__in=scores_by_attraction.keys()
        )
        to_update = []

        for prop in properties:
            prop.review_scores = scores_by_attraction[prop.id]
            to_update.append(prop)

        if to_update:
            RentalProperty.objects.bulk_update(to_update, ["review_scores"])


# Handles price snapshots from the search feed.
class PriceHistoryDBService:

    @staticmethod
    def save_prices(rows):
        if not rows:
            return

        for row in rows:
            PartitionManager.ensure_partition(
                PriceHistory, row.get("country_code")
            )

        PriceHistory.objects.bulk_insert(rows)
