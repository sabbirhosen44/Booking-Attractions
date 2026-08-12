import json


class LocationMapper:

    def __init__(
        self,
        country_map_file,
        tier_region_continent_map_file,
    ):
        self.country_map = self._load_country_map(
            country_map_file
        )
        self.location_map = self._load_location_map(
            tier_region_continent_map_file
        )

    def transform(self, country_code):
        code = self._normalize_code(country_code)

        country = self.country_map.get(code, "void")
        location = self.location_map.get(code, {})

        return {
            "country": country,
            "continent": self._value(
                location.get("continent_code")
            ),
            "tier": self._value(
                location.get("tier_dest")
            ),
            "region": self._value(
                location.get("region")
            ),
        }

    def _load_country_map(self, file_path):
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return self._build_country_map(data)

    def _load_location_map(self, file_path):
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return {
            str(code).upper(): value
            for code, value in data.items()
        }

    def _build_country_map(self, data):
        country_map = {}

        for item in data:
            code = item.get("Code")
            name = item.get("Name")

            if not code or not name:
                continue

            country_map[code.upper()] = name

        return country_map

    def _normalize_code(self, country_code):
        if not country_code:
            return ""

        return str(country_code).strip().upper()

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return value