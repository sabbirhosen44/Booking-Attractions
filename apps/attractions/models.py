from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BrinIndex, GinIndex, HashIndex
from django.db import models
from django.utils.translation import gettext_lazy as _
from psqlextra.models import PostgresPartitionedModel, PostgresModel
from psqlextra.types import PostgresPartitioningMethod


class Feed(models.TextChoices):
    BOOKING = '11', _('Booking')
    VRBO = '12', _('VRBO')
    HOTELS = '14', _('Hotels')
    AIRBNB = '16', _('AirBnb')
    TRIP = '20', _('Trip')
    HOMETOGO = '22', _('HomeToGo')
    KAYAK = '23', _('Kayak')
    EXPEDIA = '24', _('Expedia')
    LEAVETOWN = '25', _('LeaveTown')
    HOTELPLANNER = '26', _('HotelPlanner')
    VIO = '27', _('Vio')
    HOLIBOB = '101', _('Holibob')
    VIATOR = '102', _('Viator')
    BOOKING_ATTRACTION = '111', _('Booking Attraction')


class RentalProperty(PostgresModel):
    """
        Param: policy
        Value: cancellation_policy: str
               infant_policy: str
               child_policy: str
               adult_policy: str
               pet_policy: str
               event_policy: str
               checkin_policy: str
               checkout_policy: str
               payment_policy: str
               other_policies: list

        Param: property_flags
        Value: eco_friendly
               adult_only
               is_bookable
               is_business_travel
               is_monthly_stays
               is_pet_friendly
               is_preferred
               is_short_term_stays
               is_summer
               is_winter
               is_pickleball_type
               is_ski_type
               is_hotel_type
               is_other_type
               is_villa_type
               is_cabin_type
               is_cottage_type
               is_promoting_escort
               is_perfect_for_wedding
               instant_book
               has_cancellation_policy
               is_all_inclusive
               is_premier_host
               is_timeshare_type
               is_located_in_metropolitan_area

        Param: review_scores
        Value: cleanliness: float
            comfort: float
            facilities: float
            free_wifi: float
            location: float
            staff: float
            value_for_money: float

        Param: distances
        Value: airport
            beach
            lake
            next_city
            public_transport
            restaurant
            sea
            shopping
            sports
            water
        """
    id = models.CharField(primary_key=True, max_length=20)
    amenities = ArrayField(models.CharField(max_length=50), null=True)
    themes = ArrayField(models.CharField(max_length=50, blank=True, null=True), blank=True, null=True)
    amenity_categories = ArrayField(models.CharField(max_length=50), null=True)
    activities = ArrayField(models.CharField(max_length=50), null=True)
    activity_categories = ArrayField(models.CharField(max_length=50), null=True)
    archived = ArrayField(models.CharField(max_length=10), blank=True, null=True)
    bathroom_count = models.IntegerField(default=0)
    bedroom_count = models.IntegerField(default=0, db_index=True)
    bedrooms = ArrayField(models.IntegerField(default=0), blank=True, null=True)
    brand_id = models.IntegerField(default=0)
    policy = models.JSONField(blank=True, null=True)
    check_in = models.CharField(blank=True, null=True, max_length=20)
    check_out = models.CharField(blank=True, null=True, max_length=20)
    zip_code = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=250, blank=True, null=True)
    state = models.CharField(max_length=250, blank=True, null=True)
    state_abbr = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    display = models.CharField(max_length=500, blank=True, null=True)
    location_id = models.CharField(max_length=500, blank=True, null=True)
    location_walk_scores = models.JSONField(null=True, blank=True)
    partner_location_id = models.CharField(max_length=20, blank=True, null=True)
    location_assign_retry = models.IntegerField(default=0)
    parent_path = ArrayField(models.CharField(max_length=20), null=True)
    partner_country_code = models.CharField(max_length=2, blank=True, null=True)
    partner_location = models.CharField(max_length=500, blank=True, null=True)
    categories = models.TextField(blank=True, null=True)
    feature_image = models.URLField(max_length=500, blank=True, null=True)
    s3_feature_image = models.URLField(max_length=300, blank=True, null=True)
    feed = models.IntegerField(db_index=True, default=0)
    feed_provider_id = models.CharField(max_length=20, db_index=True, blank=True, null=True)
    quality_score_general = models.IntegerField(db_index=True, default=0)
    feed_provider_url = models.URLField(max_length=600, blank=True, null=True)
    languages = ArrayField(models.CharField(max_length=10), blank=True, null=True)
    latlon = gis_models.PointField(srid=4326, blank=True, null=True, spatial_index=True)
    geography_latlon = gis_models.PointField(srid=4326, geography=True, blank=True, null=True, spatial_index=True)
    max_occupancy = models.IntegerField(default=0)
    min_stay = models.IntegerField(db_index=True, default=0)
    minimum_confidence = models.FloatField(db_index=True, default=0.0)
    conversion_value = models.FloatField(default=0.0)
    conversions = models.IntegerField(default=0)
    sessions = models.IntegerField(default=0)
    property_score = models.FloatField(default=0.0)
    ml_property_score = models.FloatField(default=0.0)
    number_of_review = models.IntegerField(db_index=True, default=0)
    occupancy = models.IntegerField(db_index=True, default=0)
    online_ticket = models.BooleanField(db_index=True, default=False)
    event_duration = models.CharField(max_length=100, blank=True, null=True)
    supported_languages = models.CharField(max_length=250, blank=True, null=True)
    owner_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    booking_id = models.CharField(max_length=100, blank=True, null=True)
    vrbo_id = models.CharField(max_length=100, blank=True, null=True)
    hcom_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    airbnb_id = models.CharField(max_length=100, blank=True, null=True)
    hometogo_id = models.CharField(max_length=100, blank=True, null=True)
    kayak_id = models.IntegerField(blank=True, null=True)
    expedia_id = models.CharField(max_length=100, blank=True, null=True)
    hotelplanner_id = models.CharField(max_length=100, blank=True, null=True)
    vio_id = models.CharField(max_length=100, blank=True, null=True)
    trip_id = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.TextField(blank=True, null=True)
    listing_source_site = models.CharField(max_length=20, blank=True, null=True)
    property_name = models.CharField(max_length=450, db_index=True)
    property_type = models.CharField(max_length=40, db_index=True, blank=True, null=True)
    property_type_categories = ArrayField(models.CharField(max_length=50), null=True)
    property_type_category = models.CharField(max_length=20, db_index=True, blank=True, null=True)
    review_score_general = models.DecimalField(db_index=True, max_digits=5, decimal_places=2, default=0.0)
    review_score = models.FloatField(default=0.0)
    review_scores = models.JSONField(blank=True, null=True)
    feed_provider_quality_score = models.FloatField(default=0.0)
    room_size_sqft = models.FloatField(db_index=True, default=0.0)
    room_type = models.CharField(max_length=20, blank=True, null=True)
    star_rating = models.FloatField(db_index=True, default=0.0)
    unit_number = models.IntegerField(default=0)
    currency = models.CharField(max_length=5, blank=True, null=True)
    usd_price = models.FloatField(db_index=True, default=0.0)
    price_category = models.CharField(max_length=20, blank=True, null=True)
    images = ArrayField(models.URLField(max_length=500), blank=True, null=True, size=15)
    s3_images = ArrayField(models.URLField(max_length=300), blank=True, null=True, db_index=True, size=15)
    pickleball_court_count = models.IntegerField(default=0)
    golf_count = models.IntegerField(default=0)
    uploaded_image_count = models.IntegerField(default=0, db_index=True)
    image_quality_score = models.FloatField(default=0.0)
    cluster_id = models.CharField(max_length=15, db_index=True, blank=True, null=True)
    cluster_id_json = models.JSONField(blank=True, null=True)
    cluster_pos = models.CharField(max_length=15, blank=True, null=True)
    cluster_updated_at = models.DateTimeField(db_index=True, blank=True, null=True)
    ranked_image = models.URLField(max_length=500, blank=True, null=True)
    property_slug = models.SlugField(max_length=150, blank=True, null=True)
    complex_id = models.CharField(max_length=300, db_index=True, null=True, blank=True)
    complex_name = models.CharField(max_length=300, blank=True, null=True)
    duplicate_complex_id = models.CharField(max_length=300, blank=True, null=True)
    partners_url = models.JSONField(blank=True, null=True)
    distance_from_center_miles = models.CharField(max_length=10, blank=True, null=True)
    distances = models.JSONField(blank=True, null=True)
    property_manager = models.JSONField(blank=True, null=True)
    host_type = models.CharField(max_length=40, blank=True, null=True)
    property_attributes = ArrayField(models.CharField(max_length=50), blank=True, null=True)
    chain_and_brand = models.JSONField(blank=True, null=True)
    commission = models.JSONField(blank=True, null=True)
    meal_plan = ArrayField(models.CharField(max_length=50, blank=True, null=True), blank=True, null=True)
    duplicate_id = models.CharField(max_length=20, blank=True, null=True)
    duplicate_detect_timestamp = models.DateTimeField(db_index=True, blank=True, null=True)
    property_flags = models.JSONField(blank=True, null=True)
    has_s3_url = models.BooleanField(default=False, db_index=True)
    synced_in_efs = models.BooleanField(default=False, db_index=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=False, db_index=True)
    published = models.BooleanField(db_index=True, default=False)
    is_deleted = models.BooleanField(default=False, db_index=True)
    is_expired = models.BooleanField(default=False, db_index=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)
    property_live_date = models.DateTimeField(db_index=True, blank=True, null=True)
    property_modified_date = models.DateTimeField(db_index=True, blank=True, null=True)
    property_highlights_map = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "rental_property"
        indexes = (
            BrinIndex(fields=['created_at']),
            GinIndex(fields=['property_flags']),
            GinIndex(fields=['property_type_categories']),
            GinIndex(fields=['parent_path']),
            GinIndex(fields=['amenities']),
            GinIndex(fields=['amenity_categories']),
            GinIndex(fields=['activities']),
            GinIndex(fields=['activity_categories']),
            HashIndex(fields=['country_code']),
            HashIndex(fields=['state_abbr']),
            GinIndex(fields=['archived'])
        )
        verbose_name, verbose_name_plural = "Rental Property", "Rental Properties"


class PropertyImageMeta(PostgresPartitionedModel):
    """
    Param: predictions
    Value: [label]: float
    """

    property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, )
    feed = models.CharField(max_length=5, choices=Feed.choices)
    url = models.URLField(max_length=500)
    path = models.CharField(max_length=500, db_index=True, null=True, blank=True)
    label = models.CharField(max_length=30, db_index=True, blank=True, null=True)
    captions = models.CharField(max_length=600, null=True, blank=True)
    confidence = models.FloatField(db_index=True, default=0.0)
    image_quality_score = models.FloatField(default=0.0)
    predictions = models.JSONField(null=True, blank=True)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    s3_url = models.URLField(max_length=300, blank=True, null=True)
    has_s3_url = models.BooleanField(default=False, db_index=True)
    is_vector_generated = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        db_table = "property_image_meta"
        verbose_name, verbose_name_plural = "Property Image Meta", "Properties Image Meta"
        unique_together = ('property_id', 'path', 'country_code')
        indexes = (
            HashIndex(fields=['country_code']),
        )

    class PartitioningMeta:
        method = PostgresPartitioningMethod.LIST
        key = ['country_code']


class PropertyReviews(PostgresPartitionedModel):
    """
    Param: reviewer
    Value: country: "US"
           name: "Carl"
           travel_purpose: "Leisure"
           type: "Couple"
           profile_photo: "https://a0.muscache.com/defaults/user_pic-50x50.png?v=3"
    """

    id = models.CharField(primary_key=True, max_length=50)
    property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, )
    feed = models.CharField(max_length=5, choices=Feed.choices)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    language_code = models.CharField(max_length=3, default="en")
    score = models.FloatField(default=0, null=False)
    summary = models.TextField(blank=True, null=True)
    negative = models.TextField(blank=True, null=True)
    positive = models.TextField(blank=True, null=True)
    reviewer = models.JSONField(blank=True, null=True)
    review_date = models.DateTimeField(blank=True, null=True)
    checkin_date = models.DateTimeField(blank=True, null=True)
    checkout_date = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        db_table = "property_reviews"
        verbose_name, verbose_name_plural = "Property Review", "Property Reviews"

        indexes = (
            HashIndex(fields=['language_code']),
            HashIndex(fields=['country_code']),
        )

    class PartitioningMeta:
        method = PostgresPartitioningMethod.LIST
        key = ['country_code']


class RentalPropertyLocalize(PostgresPartitionedModel):
    """
    Param: captions
    Value: caption: str
           url: str

    Param: feature_summary
    Value: description: text
           name : str

    Param: policies
    Value: adult_policy: text
           cancellation_policy: text
           checkin_policy: text
           checkout_policy: text
           child_policy: text
           event_policy: text
           infant_policy: text
           other_policy: text
           payment_policy: text
           pet_policy: text
           smoking_policy: text

    Param: room_arrangement
    Value: attributes
           bed_options
           facilities
           id
           maximum_occupancy
                adults
                children
                total_guests
           name
           number_of_rooms
                bathrooms
                bedrooms
                living_rooms
           photos
           room_type
           size
           usd_rate
    """

    class PartitioningMeta:
        method = PostgresPartitioningMethod.LIST
        key = ['country_code']

    property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, )
    address = models.CharField(max_length=500, blank=True, null=True)
    captions = models.JSONField(blank=True, null=True)
    display = models.CharField(max_length=500, blank=True, null=True)
    feature_summary = models.JSONField(blank=True, null=True)
    feed = models.IntegerField(db_index=True, default=0)
    language = models.CharField(max_length=50)
    policies = models.JSONField(blank=True, null=True)
    property_description = models.TextField(blank=True, null=True)
    area_description = models.TextField(blank=True, null=True)
    property_name = models.CharField(max_length=450, blank=True, null=True)
    property_type = models.CharField(max_length=40, blank=True, null=True)
    room_arrangement = models.JSONField(blank=True, null=True)
    property_slug = models.SlugField(max_length=150, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    is_translated = models.BooleanField(default=False, db_index=True, )
    created_at = models.DateTimeField(blank=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        db_table = "rental_property_localize"
        ordering = ['-id']
        verbose_name, verbose_name_plural = "Rental Property Localize", "Rentals Properties Localize"

        indexes = (
            HashIndex(fields=['language']),
            HashIndex(fields=['country_code'])
        )
        unique_together = ('property_id', 'language', 'country_code')


class PriceHistory(PostgresPartitionedModel):
    class PartitioningMeta:
        method = PostgresPartitioningMethod.LIST
        key = ['country_code']

    property = models.ForeignKey(RentalProperty, on_delete=models.CASCADE, )
    price = models.JSONField(null=True, db_index=True)
    check_in = models.DateField(blank=True, null=True, db_index=True)
    check_out = models.DateField(blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    feed = models.CharField(max_length=5, choices=Feed.choices)
    country_code = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        db_table = "price_history"
        indexes = (
            HashIndex(fields=['country_code']),
        )


class Location(models.Model):
    """
        Param: aggregation_counts
        Value:
            total_count: int,
            average_price: float,
            average_room_size: float,
            eco_friendly_count: int
        Param: property_type_categories_count
        Value: {key: str, doc_count: int} | key: property_type_category
        Param: amenity_categories_count
        Value: {key: str, doc_count: int} | key: amenity_category
        Param: category_section_property_count
        Value:
            htl: cheap: int
                 luxury: int
                 nearby: int
                 top_rated: int
                 pet_friendly: int
                 all_inclusive: int
                 last_minute_book: int
                 vr_villa_hotel_suites: int
            vhr: cheap: int
                 luxury: int
                 nearby: int
                 top_rated: int
                 pet_friendly: int
                 all_inclusive: int
                 last_minute_book: int
                 vr_villa_hotel_suites: int
            common: luxury: int
                    top_rated: int
                    pet_friendly: int
                    large_vacation: int
                    instant_bookable: int
                    usd_price_under_200: int
                    wheelchair_accessible: int
            pet:    luxury: int
                    top_rated: int
                    pet_friendly: int
                    large_vacation: int
                    instant_bookable: int
                    usd_price_under_200: int
                    wheelchair_accessible: int
    """
    id = models.CharField(primary_key=True, max_length=20)
    ancestors = models.JSONField()
    bounding_polygon = gis_models.GeometryField(spatial_index=True, srid=4326, null=True)
    breadcrumbs = models.JSONField()
    state_abbr = models.CharField(max_length=3, blank=True, null=True)
    center = gis_models.PointField(srid=4326, spatial_index=True)
    geography_center = gis_models.PointField(srid=4326, geography=True, spatial_index=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    display_list = ArrayField(models.CharField(max_length=120))
    google_place_id = models.CharField(max_length=150, blank=True, null=True, )
    slug = models.SlugField(max_length=150)
    bc_location_id = models.CharField(max_length=20, blank=True, null=True)
    hg_location_id = models.CharField(max_length=20, blank=True, null=True, )
    tc_location_id = models.CharField(max_length=20, blank=True, null=True)
    is_verification_required = models.BooleanField(default=False, db_index=True)
    is_metropolitan_area = models.BooleanField(default=False, db_index=True)
    location_level = models.IntegerField(default=0, db_index=True)
    location_type = models.CharField(max_length=30)
    location_types = ArrayField(models.CharField(max_length=30), default=list)
    name = models.CharField(max_length=250, db_index=True)
    nearby_location = models.JSONField(blank=True, null=True, )
    nearby_transportation = models.JSONField(blank=True, null=True, )
    neighborhood = models.JSONField(blank=True, null=True, )
    parent_id = models.CharField(max_length=20)
    parent_path = ArrayField(models.CharField(max_length=20))
    point_of_interest = models.JSONField(null=True, blank=True)
    property_count = models.IntegerField(default=0, db_index=True)
    property_count_by_distances = models.JSONField(blank=True, null=True)
    property_count_by_radius = models.IntegerField(default=0, db_index=True)
    property_count_by_feed = models.JSONField(blank=True, null=True, )
    activity_count = models.IntegerField(default=0, db_index=True)
    activity_count_by_distances = models.JSONField(blank=True, null=True)
    activity_count_by_radius = models.IntegerField(default=0, db_index=True)
    radius = models.FloatField(default=0)
    short_name = models.CharField(max_length=150, db_index=True)
    type_level = models.IntegerField(default=0, db_index=True)
    category_section_property_count = models.JSONField(null=True, blank=True)
    amenity_categories_count = models.JSONField(null=True, blank=True)
    property_type_categories_count = models.JSONField(null=True, blank=True)
    aggregation_counts = models.JSONField(null=True, blank=True)
    languages = ArrayField(models.CharField(max_length=10), blank=True, null=True)
    feature_image = models.URLField(max_length=500, blank=True, null=True)
    conversion_value = models.FloatField(default=0.0)
    conversions = models.IntegerField(default=0)
    sessions = models.IntegerField(default=0)
    location_score = models.FloatField(default=0.0)
    walk_scores = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, db_index=True)


class SkipProperties(models.Model):
    property_id = models.CharField(max_length=20, unique=True)
    feed = models.CharField(max_length=50, choices=Feed.choices)
    reason = models.TextField(blank=True, null=True)
    location_id = models.CharField(max_length=500, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "skip_properties"
        verbose_name, verbose_name_plural = "Skip Property", "Skip Properties"