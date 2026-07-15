from django.contrib.gis.geos import Point
from django.utils.text import slugify

from apps.attractions.models import Feed
from core.utils.location_resolver import LocationResolver
from core.utils.country_resolver import CountryResolver


class AttractionRowBuilder:

    MAX_IMAGES = 15
    MAX_SLUG_LENGTH = 150

    def __init__(self, location_resolver=None, country_resolver=None):
        self.location_resolver = location_resolver or LocationResolver()
        self.country_resolver = country_resolver or CountryResolver()

    @staticmethod
    def _pick_primary_location(locations):
        if not locations:
            return {}
        for location in locations:
            if location.get("type") == "departure":
                return location
        return locations[0]

    @staticmethod
    def _first_locale_value(mapping):
        if not mapping:
            return None
        if "en-us" in mapping:
            return mapping["en-us"]
        return next(iter(mapping.values()), None)

    @staticmethod
    def _build_point(coordinates):
        if not coordinates:
            return None
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")
        if latitude is None or longitude is None:
            return None
        try:
            return Point(float(longitude), float(latitude), srid=4326)
        except (TypeError, ValueError):
            return None

    @classmethod
    def _build_slug(cls, name):
        slug = slugify(name)
        if not slug:
            return None
        if len(slug) > cls.MAX_SLUG_LENGTH:
            slug = slug[: cls.MAX_SLUG_LENGTH].rstrip("-")
        return slug or None

    def _resolve_city(self, country_code, city_code):
        if city_code is None:
            return None
        return self.location_resolver.resolve(country_code, city_code)

    def build(self, item):
        attraction_id = item["id"]
        names = item.get("name", {}) or {}
        descriptions = item.get("long_description", {}) or {}
        locations = item.get("locations", []) or []
        primary_location = self._pick_primary_location(locations)

        country_code = (primary_location.get("country") or "xx").lower()
        city_code = primary_location.get("city")
        point = self._build_point(primary_location.get("coordinates"))

        ratings = item.get("ratings", {}) or {}
        urls = item.get("urls", {}) or {}
        web_urls = urls.get("web", {}) or {}
        app_urls = urls.get("app", {}) or {}

        property_name = self._first_locale_value(names) or attraction_id
        supported_languages = item.get("supported_languages", []) or []
        photo_urls = [
            photo["url"]
            for photo in (item.get("photos", []) or [])
            if photo.get("url")
        ]

        property_slug = self._build_slug(property_name)

        property_row = {
            "id": attraction_id,
            "booking_id": attraction_id,
            "feed": int(Feed.BOOKING_ATTRACTION),
            "property_name": property_name,
            "property_slug": property_slug,
            "property_type": "attraction",
            "activity_categories": item.get("categories", []) or [],
            "property_attributes": item.get("badges", []) or [],
            "review_score_general": ratings.get("score"),
            "review_score": ratings.get("score"),
            "number_of_review": ratings.get("number_of_reviews"),
            "languages": supported_languages,
            "supported_languages": ",".join(supported_languages),
            "images": photo_urls[: self.MAX_IMAGES],
            "uploaded_image_count": len(photo_urls),
            "feed_provider_url": web_urls.get("detail"),
            "partners_url": {
                "web": web_urls.get("detail"),
                "app": app_urls.get("detail"),
            },
            "display": primary_location.get("address"),
            "zip_code": primary_location.get("post_code"),
            "country_code": country_code,
            "country": self.country_resolver.resolve(country_code),
            "city": self._resolve_city(country_code, city_code),
            "location_id": str(city_code) if city_code is not None else None,
            "latlon": point,
            "geography_latlon": point,
        }

        localized_rows = []
        for lang, name in names.items():
            localized_rows.append(
                {
                    "property_id": attraction_id,
                    "feed": int(Feed.BOOKING_ATTRACTION),
                    "language": lang,
                    "property_name": name,
                    "property_description": descriptions.get(lang),
                    "property_slug": property_slug,
                    "property_type": "attraction",
                    "address": primary_location.get("address"),
                    "country_code": country_code,
                }
            )

        photo_rows = []
        for url in photo_urls:
            photo_rows.append(
                {
                    "property_id": attraction_id,
                    "feed": Feed.BOOKING_ATTRACTION,
                    "url": url,
                    "country_code": country_code,
                }
            )

        return property_row, localized_rows, photo_rows