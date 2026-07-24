from datetime import datetime, timezone
from typing import Optional

from core.utils.location_mapping_reader import LocationMappingReader
from core.utils.slug_util import SlugUtil
from vector_etl.schema_aligner import SchemaAligner


def _truncate(value: Optional[str], length: int) -> Optional[str]:
    if value is None:
        return None
    return value[:length]


def _pick_primary_location(record: dict) -> dict:
    locations = record.get("locations") or []
    if not locations:
        return {}
    for loc in locations:
        if loc.get("type") == "departure":
            return loc
    return locations[0]


# Builds the full 119-field rental_property payload stored next to each vector
class RentalPropertyPayloadBuilder:
    def __init__(self, location_lookup: LocationMappingReader):
        self.location_lookup = location_lookup

    def build(self, record: dict) -> dict:
        loc = _pick_primary_location(record)
        country_code = (loc.get("country") or "xx").lower()
        city_code = loc.get("city")
        city_name = self.location_lookup.resolve(country_code, city_code)

        name_map = record.get("name") or {}
        property_name = name_map.get("en-us") or (next(iter(name_map.values()), None)) or record["id"]

        photos = record.get("photos") or []
        photo_urls = [p.get("url") for p in photos if p.get("url")]

        lat = (loc.get("coordinates") or {}).get("latitude")
        lon = (loc.get("coordinates") or {}).get("longitude")
        geo_point = {"lat": lat, "lon": lon} if lat is not None and lon is not None else None

        ratings = record.get("ratings") or {}
        urls = record.get("urls") or {}
        supported_languages = record.get("supported_languages") or []

        payload = {
            "id": record["id"],
            "booking_id": _truncate(record["id"], 100),
            "feed": 111,
            "property_name": _truncate(property_name, 450),
            "property_slug": SlugUtil.slugify(property_name),
            "property_type": "attraction",
            "activity_categories": record.get("categories") or [],
            "property_attributes": record.get("badges") or [],
            "review_score_general": ratings.get("score"),
            "review_score": ratings.get("score"),
            "number_of_review": ratings.get("number_of_reviews"),
            "languages": supported_languages,
            "supported_languages": _truncate(",".join(supported_languages), 250),
            "images": photo_urls[:15],
            "uploaded_image_count": len(photo_urls),
            "feed_provider_url": _truncate((urls.get("web") or {}).get("detail"), 600),
            "partners_url": {
                "web": (urls.get("web") or {}).get("detail"),
                "app": (urls.get("app") or {}).get("detail"),
            },
            "display": _truncate(loc.get("address"), 500),
            "zip_code": _truncate(loc.get("post_code"), 50),
            "country_code": country_code,
            "city": _truncate(city_name, 250),
            "location_id": _truncate(str(city_code) if city_code is not None else None, 500),
            "latlon": geo_point,
            "geography_latlon": geo_point,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        return SchemaAligner.align(payload)