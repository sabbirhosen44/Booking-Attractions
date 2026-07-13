import json
import threading

from core.utils.import_config import ImportConfig


# Resolves Booking Attractions numeric location codes (city, district,landmark, region) into human-readable names using the static

class LocationResolver:

    _FILES = (
        ("city.json", "city_code", "city"),
        ("district.json", "district_code", "district"),
        ("landmark.json", "landmark_code", "landmark"),
        ("region.json", "region_code", "region"),
    )

    def __init__(self, config=ImportConfig):
        self.config = config
        self._cache = {}
        self._lock = threading.Lock()

    def _load_country(self, country_code):
        country_code = (country_code or "").lower()

        if country_code in self._cache:
            return self._cache[country_code]

        with self._lock:
            if country_code in self._cache:
                return self._cache[country_code]

            merged = {}
            base = (
                self.config.DATA_DIR
                / "static"
                / "location_mapping"
                / country_code
            )

            for filename, code_key, name_key in self._FILES:
                file_path = base / filename

                if not file_path.exists():
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        entries = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

                for entry in entries:
                    code = entry.get(code_key)
                    name = entry.get(name_key)

                    if code is None or name is None:
                        continue

                    key = str(code)
                    if key not in merged:
                        merged[key] = name

            self._cache[country_code] = merged

            return merged

    def resolve(self, country_code, location_code):
        if location_code is None:
            return None

        mapping = self._load_country(country_code)

        return mapping.get(str(location_code))
