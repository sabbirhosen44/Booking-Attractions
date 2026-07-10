from attractions.models import (
    Attraction,
    AttractionLocalized,
    AttractionPhoto,
    AttractionReview,
    AttractionReviewScore,
)

# Handles all database operations related to attractions,localized content and attraction photos.
class AttractionDBService:

    @staticmethod
    def save_attractions(rows):
        if not rows:
            return

        Attraction.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=[
                "duration",
                "rating_score",
                "rating_review_count",
                "categories",
                "badges",
                "booking_web_url",
                "booking_app_url",
                "city_id",
                "country_code",
                "latitude",
                "longitude",
                "address",
                "post_code",
                "location_type",
            ],
        )

    @staticmethod
    def save_localized(rows):
        if not rows:
            return

        AttractionLocalized.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=[
                "attraction",
                "language_code",
            ],
            update_fields=[
                "name",
                "description",
            ],
        )

    @staticmethod
    def save_photos(rows):
        if not rows:
            return

        AttractionPhoto.objects.bulk_create(
            rows,
            ignore_conflicts=True,
        )

    @staticmethod
    def get_existing_attraction_ids():
        return set(
            Attraction.objects.values_list(
                "id",
                flat=True,
            )
        )

# Handles all database operations related to attraction reviews.
class ReviewDBService:

    @staticmethod
    def save_reviews(rows):
        if not rows:
            return

        AttractionReview.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=[
                "author_name",
                "author_country_code",
                "rating",
                "review_text",
                "language_code",
                "review_date",
            ],
        )

# Handles all database operations related to review score breakdowns.
class ReviewScoreDBService:

    @staticmethod
    def save_scores(rows):
        if not rows:
            return

        AttractionReviewScore.objects.bulk_create(
            rows,
            update_conflicts=True,
            unique_fields=[
                "attraction",
                "score_type",
            ],
            update_fields=[
                "score",
                "review_count",
            ],
        )