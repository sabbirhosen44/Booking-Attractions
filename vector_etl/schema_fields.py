# Full field list for rental_property, mirrors apps/attractions/models.py
# exactly - same list as dynamodb_etl/tables/schema_fields.py's entry
# for this table. No property_description here - that field only exists
# on RentalPropertyLocalize, a different table this pipeline never touches.

RENTAL_PROPERTY_FIELDS = [
    "id", "amenities", "themes", "amenity_categories", "activities",
    "activity_categories", "archived", "bathroom_count", "bedroom_count",
    "bedrooms", "brand_id", "policy", "check_in", "check_out", "zip_code",
    "city", "state", "state_abbr", "country", "country_code", "display",
    "location_id", "location_walk_scores", "partner_location_id",
    "location_assign_retry", "parent_path", "partner_country_code",
    "partner_location", "categories", "feature_image", "s3_feature_image",
    "feed", "feed_provider_id", "quality_score_general", "feed_provider_url",
    "languages", "latlon", "geography_latlon", "max_occupancy", "min_stay",
    "minimum_confidence", "conversion_value", "conversions", "sessions",
    "property_score", "ml_property_score", "number_of_review", "occupancy",
    "online_ticket", "event_duration", "supported_languages", "owner_id",
    "booking_id", "vrbo_id", "hcom_id", "airbnb_id", "hometogo_id",
    "kayak_id", "expedia_id", "hotelplanner_id", "vio_id", "trip_id",
    "license_number", "listing_source_site", "property_name",
    "property_type", "property_type_categories", "property_type_category",
    "review_score_general", "review_score", "review_scores",
    "feed_provider_quality_score", "room_size_sqft", "room_type",
    "star_rating", "unit_number", "currency", "usd_price", "price_category",
    "images", "s3_images", "pickleball_court_count", "golf_count",
    "uploaded_image_count", "image_quality_score", "cluster_id",
    "cluster_id_json", "cluster_pos", "cluster_updated_at", "ranked_image",
    "property_slug", "complex_id", "complex_name", "duplicate_complex_id",
    "partners_url", "distance_from_center_miles", "distances",
    "property_manager", "host_type", "property_attributes",
    "chain_and_brand", "commission", "meal_plan", "duplicate_id",
    "duplicate_detect_timestamp", "property_flags", "has_s3_url",
    "synced_in_efs", "phone_number", "is_active", "published",
    "is_deleted", "is_expired", "updated_by", "created_at", "updated_at",
    "property_live_date", "property_modified_date", "property_highlights_map",
]