from datetime import datetime, timezone
from typing import Optional

from elasticsearch_etl.readers.location_mapping_reader import LocationMappingReader
from elasticsearch_etl.transforms.slug import SlugUtil


# Builds property, localize, and image docs from one attraction record
class RentalPropertyTransform:
    def __init__(self, location_lookup: LocationMappingReader):
        self.location_lookup = location_lookup

    @staticmethod
    def _truncate(value: Optional[str], length: int) -> Optional[str]:
        if value is None:
            return None
        return value[:length]

    @staticmethod
    def _pick_primary_location(record: dict) -> dict:
        locations = record.get("locations") or []
        if not locations:
            return {}
        for loc in locations:
            if loc.get("type") == "departure":
                return loc
        return locations[0]

    def build_property_doc(self, record: dict) -> dict:
        loc = self._pick_primary_location(record)
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

        return {
            "id": record["id"],
            "booking_id": self._truncate(record["id"], 100),
            "feed": 111,
            "property_name": self._truncate(property_name, 450),
            "property_slug": SlugUtil.slugify(property_name),
            "property_type": "attraction",
            "activity_categories": record.get("categories") or [],
            "property_attributes": record.get("badges") or [],
            "review_score_general": ratings.get("score"),
            "review_score": ratings.get("score"),
            "number_of_review": ratings.get("number_of_reviews"),
            "languages": supported_languages,
            "supported_languages": self._truncate(",".join(supported_languages), 250),
            "images": photo_urls[:15],
            "uploaded_image_count": len(photo_urls),
            "feed_provider_url": self._truncate((urls.get("web") or {}).get("detail"), 600),
            "partners_url": {
                "web": (urls.get("web") or {}).get("detail"),
                "app": (urls.get("app") or {}).get("detail"),
            },
            "display": self._truncate(loc.get("address"), 500),
            "zip_code": self._truncate(loc.get("post_code"), 50),
            "country_code": country_code,
            "city": self._truncate(city_name, 250),
            "location_id": self._truncate(str(city_code) if city_code is not None else None, 500),
            "latlon": geo_point,
            "geography_latlon": geo_point,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def build_localize_docs(self, record: dict, property_slug: str) -> list[dict]:
        loc = self._pick_primary_location(record)
        country_code = (loc.get("country") or "xx").lower()
        name_map = record.get("name") or {}
        long_description = record.get("long_description") or {}

        docs = []
        for language, name in name_map.items():
            docs.append({
                "property_id": record["id"],
                "feed": 111,
                "language": self._truncate(language, 50),
                "property_name": self._truncate(name, 450),
                "property_description": long_description.get(language),
                "property_slug": property_slug,
                "property_type": "attraction",
                "address": self._truncate(loc.get("address"), 500),
                "country_code": country_code,
            })
        return docs

    def build_image_docs(self, record: dict) -> list[dict]:
        loc = self._pick_primary_location(record)
        country_code = (loc.get("country") or "xx").lower()
        photos = record.get("photos") or []

        docs = []
        for photo in photos:
            url = photo.get("url")
            if not url:
                continue
            docs.append({
                "property_id": record["id"],
                "feed": "111",
                "url": url,
                "country_code": country_code,
            })
        return docs
