from django.db import models


class Attraction(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    duration = models.CharField(max_length=255, null=True, blank=True)
    rating_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    rating_review_count = models.IntegerField(null=True, blank=True)
    categories = models.JSONField(default=list)
    badges = models.JSONField(default=list)
    booking_web_url = models.TextField(null=True, blank=True)
    booking_app_url = models.TextField(null=True, blank=True)
    city_id = models.IntegerField(null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    address = models.TextField(null=True, blank=True)
    post_code = models.CharField(max_length=20, null=True, blank=True)
    location_type = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "attractions"


class AttractionLocalized(models.Model):
    attraction = models.ForeignKey(
        Attraction,
        related_name="localized",
        on_delete=models.CASCADE,
    )
    language_code = models.CharField(max_length=10)
    name = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "attraction_localized"
        constraints = [
            models.UniqueConstraint(
                fields=["attraction", "language_code"],
                name="uq_localized_attraction_language",
            ),
        ]


class AttractionPhoto(models.Model):
    attraction = models.ForeignKey(
        Attraction,
        related_name="photos",
        on_delete=models.CASCADE,
    )
    photo_url = models.TextField()

    class Meta:
        db_table = "attraction_photos"
        constraints = [
            models.UniqueConstraint(
                fields=["attraction", "photo_url"],
                name="uq_photos_attraction_url",
            ),
        ]


class AttractionReview(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    attraction = models.ForeignKey(
        Attraction,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    author_name = models.CharField(max_length=255, null=True, blank=True)
    author_country_code = models.CharField(
        max_length=10, null=True, blank=True
    )
    rating = models.IntegerField(null=True, blank=True)
    review_text = models.TextField(null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "attraction_reviews"


class AttractionReviewScore(models.Model):
    attraction = models.ForeignKey(
        Attraction,
        related_name="review_scores",
        on_delete=models.CASCADE,
    )
    score_type = models.CharField(max_length=255)
    score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    review_count = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "attraction_review_scores"
        constraints = [
            models.UniqueConstraint(
                fields=["attraction", "score_type"],
                name="uq_scores_attraction_type",
            ),
        ]