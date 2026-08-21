from core.utils.location_id_generator import LocationIDGenerator


class LocationRowBuilder:

    @classmethod
    def build(cls, latlon, geography_latlon):
        if not latlon:
            return None

        return {
            "id": LocationIDGenerator.generate(),
            "ancestors": [],
            "bounding_polygon": None,
            "breadcrumbs": [],
            "display_list": [],
            "slug": "",
            "location_type": "",
            "location_types": [],
            "name": "",
            "parent_id": "",
            "parent_path": [],
            "short_name": "",
            "center": latlon,
            "geography_center": geography_latlon,
        }