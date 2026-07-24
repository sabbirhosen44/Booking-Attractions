from typing import Optional

from core.utils.location_mapping_reader import LocationMappingReader
from core.utils.slug_util import SlugUtil


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


# Builds the metadata payload stored next to each vector in Qdrant
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
        feature_image = photos[0].get("url") if photos else None

        ratings = record.get("ratings") or {}

        return {
            "property_id": record["id"],
            "property_name": _truncate(property_name, 450),
            "property_slug": SlugUtil.slugify(property_name),
            "city": _truncate(city_name, 250),
            "country_code": country_code,
            "categories": record.get("categories") or [],
            "review_score_general": ratings.get("score"),
            "feature_image": feature_image,
            "display": _truncate(loc.get("address"), 500),
        }
