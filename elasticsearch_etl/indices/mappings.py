# Mirrors apps/attractions/models.py field-for-field

KEYWORD = {"type": "keyword"}
TEXT = {"type": "text"}
INTEGER = {"type": "integer"}
FLOAT = {"type": "float"}
BOOLEAN = {"type": "boolean"}
DATE = {"type": "date"}
OBJECT = {"type": "object", "dynamic": True, "enabled": True}
GEO_POINT = {"type": "geo_point"}


def _scaled_float(decimal_places: int = 2):
    return {"type": "scaled_float", "scaling_factor": 10 ** decimal_places}


RENTAL_PROPERTY_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "amenities": KEYWORD,
        "themes": KEYWORD,
        "amenity_categories": KEYWORD,
        "activities": KEYWORD,
        "activity_categories": KEYWORD,
        "archived": KEYWORD,
        "bathroom_count": INTEGER,
        "bedroom_count": INTEGER,
        "bedrooms": INTEGER,
        "brand_id": INTEGER,
        "policy": OBJECT,
        "check_in": KEYWORD,
        "check_out": KEYWORD,
        "zip_code": KEYWORD,
        "city": KEYWORD,
        "state": KEYWORD,
        "state_abbr": KEYWORD,
        "country": KEYWORD,
        "country_code": KEYWORD,
        "display": TEXT,
        "location_id": KEYWORD,
        "location_walk_scores": OBJECT,
        "partner_location_id": KEYWORD,
        "location_assign_retry": INTEGER,
        "parent_path": KEYWORD,
        "partner_country_code": KEYWORD,
        "partner_location": KEYWORD,
        "categories": TEXT,
        "feature_image": KEYWORD,
        "s3_feature_image": KEYWORD,
        "feed": INTEGER,
        "feed_provider_id": KEYWORD,
        "quality_score_general": INTEGER,
        "feed_provider_url": KEYWORD,
        "languages": KEYWORD,
        "latlon": GEO_POINT,
        "geography_latlon": GEO_POINT,
        "max_occupancy": INTEGER,
        "min_stay": INTEGER,
        "minimum_confidence": FLOAT,
        "conversion_value": FLOAT,
        "conversions": INTEGER,
        "sessions": INTEGER,
        "property_score": FLOAT,
        "ml_property_score": FLOAT,
        "number_of_review": INTEGER,
        "occupancy": INTEGER,
        "online_ticket": BOOLEAN,
        "event_duration": KEYWORD,
        "supported_languages": KEYWORD,
        "owner_id": KEYWORD,
        "booking_id": KEYWORD,
        "vrbo_id": KEYWORD,
        "hcom_id": KEYWORD,
        "airbnb_id": KEYWORD,
        "hometogo_id": KEYWORD,
        "kayak_id": INTEGER,
        "expedia_id": KEYWORD,
        "hotelplanner_id": KEYWORD,
        "vio_id": KEYWORD,
        "trip_id": KEYWORD,
        "license_number": TEXT,
        "listing_source_site": KEYWORD,
        "property_name": TEXT,
        "property_type": KEYWORD,
        "property_type_categories": KEYWORD,
        "property_type_category": KEYWORD,
        "review_score_general": _scaled_float(2),
        "review_score": FLOAT,
        "review_scores": OBJECT,
        "feed_provider_quality_score": FLOAT,
        "room_size_sqft": FLOAT,
        "room_type": KEYWORD,
        "star_rating": FLOAT,
        "unit_number": INTEGER,
        "currency": KEYWORD,
        "usd_price": FLOAT,
        "price_category": KEYWORD,
        "images": KEYWORD,
        "s3_images": KEYWORD,
        "pickleball_court_count": INTEGER,
        "golf_count": INTEGER,
        "uploaded_image_count": INTEGER,
        "image_quality_score": FLOAT,
        "cluster_id": KEYWORD,
        "cluster_id_json": OBJECT,
        "cluster_pos": KEYWORD,
        "cluster_updated_at": DATE,
        "ranked_image": KEYWORD,
        "property_slug": KEYWORD,
        "complex_id": KEYWORD,
        "complex_name": KEYWORD,
        "duplicate_complex_id": KEYWORD,
        "partners_url": OBJECT,
        "distance_from_center_miles": KEYWORD,
        "distances": OBJECT,
        "property_manager": OBJECT,
        "host_type": KEYWORD,
        "property_attributes": KEYWORD,
        "chain_and_brand": OBJECT,
        "commission": OBJECT,
        "meal_plan": KEYWORD,
        "duplicate_id": KEYWORD,
        "duplicate_detect_timestamp": DATE,
        "property_flags": OBJECT,
        "has_s3_url": BOOLEAN,
        "synced_in_efs": BOOLEAN,
        "phone_number": KEYWORD,
        "is_active": BOOLEAN,
        "published": BOOLEAN,
        "is_deleted": BOOLEAN,
        "is_expired": BOOLEAN,
        "updated_by": KEYWORD,
        "created_at": DATE,
        "updated_at": DATE,
        "property_live_date": DATE,
        "property_modified_date": DATE,
        "property_highlights_map": OBJECT,
    }
}

# id here is always null, no ES autoincrement
RENTAL_PROPERTY_LOCALIZE_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "property_id": KEYWORD,
        "address": TEXT,
        "captions": OBJECT,
        "display": TEXT,
        "feature_summary": OBJECT,
        "feed": INTEGER,
        "language": KEYWORD,
        "policies": OBJECT,
        "property_description": TEXT,
        "area_description": TEXT,
        "property_name": TEXT,
        "property_type": KEYWORD,
        "room_arrangement": OBJECT,
        "property_slug": KEYWORD,
        "country_code": KEYWORD,
        "is_translated": BOOLEAN,
        "created_at": DATE,
        "updated_at": DATE,
    }
}

# path always null, no dedup key for photos
PROPERTY_IMAGE_META_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "property_id": KEYWORD,
        "feed": KEYWORD,
        "url": KEYWORD,
        "path": KEYWORD,
        "label": KEYWORD,
        "captions": TEXT,
        "confidence": FLOAT,
        "image_quality_score": FLOAT,
        "predictions": OBJECT,
        "width": INTEGER,
        "height": INTEGER,
        "country_code": KEYWORD,
        "s3_url": KEYWORD,
        "has_s3_url": BOOLEAN,
        "is_vector_generated": BOOLEAN,
        "is_deleted": BOOLEAN,
        "updated_at": DATE,
    }
}

PROPERTY_REVIEWS_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "property_id": KEYWORD,
        "feed": KEYWORD,
        "country_code": KEYWORD,
        "language_code": KEYWORD,
        "score": FLOAT,
        "summary": TEXT,
        "negative": TEXT,
        "positive": TEXT,
        "reviewer": OBJECT,
        "review_date": DATE,
        "checkin_date": DATE,
        "checkout_date": DATE,
        "updated_at": DATE,
    }
}

PRICE_HISTORY_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "property_id": KEYWORD,
        "price": OBJECT,
        "check_in": DATE,
        "check_out": DATE,
        "created_at": DATE,
        "feed": KEYWORD,
        "country_code": KEYWORD,
    }
}

SKIP_PROPERTIES_MAPPING = {
    "properties": {
        "id": KEYWORD,
        "property_id": KEYWORD,
        "feed": KEYWORD,
        "reason": TEXT,
        "location_id": KEYWORD,
        "updated_at": DATE,
        "updated_by": KEYWORD,
    }
}

INDEX_MAPPINGS = {
    "rental_property": RENTAL_PROPERTY_MAPPING,
    "rental_property_localize": RENTAL_PROPERTY_LOCALIZE_MAPPING,
    "property_image_meta": PROPERTY_IMAGE_META_MAPPING,
    "property_reviews": PROPERTY_REVIEWS_MAPPING,
    "price_history": PRICE_HISTORY_MAPPING,
    "skip_properties": SKIP_PROPERTIES_MAPPING,
}
