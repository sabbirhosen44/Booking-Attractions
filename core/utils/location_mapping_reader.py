import json
from pathlib import Path
from typing import Dict, Tuple

# Each file has its own code/name key pair, following Booking's
# {type}_code / {type} naming convention (confirmed from a real
# city.json sample: {"city_code": -3367394, "city": "Yasica Arriba"}).
FILE_KEY_MAP = {
    "city.json": ("city_code", "city"),
    "district.json": ("district_code", "district"),
    "landmark.json": ("landmark_code", "landmark"),
    "region.json": ("region_code", "region"),
}


# Resolves numeric location codes to names, city > district > landmark > region
class LocationMappingReader:
    PRIORITY_FILES = ("city.json", "district.json", "landmark.json", "region.json")

    def __init__(self, static_dir: Path):
        self._lookup: Dict[Tuple[str, str], str] = {}
        self._loaded_count = 0
        self._load(static_dir / "location_mapping")

    def _load(self, mapping_root: Path) -> None:
        if not mapping_root.exists():
            print(f"WARNING: location_mapping folder not found at {mapping_root}")
            return

        for country_dir in mapping_root.iterdir():
            if not country_dir.is_dir():
                continue
            country_code = country_dir.name.lower()

            for filename in reversed(self.PRIORITY_FILES):
                file_path = country_dir / filename
                if not file_path.exists():
                    continue

                code_key, name_key = FILE_KEY_MAP[filename]
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        entries = json.load(f)
                    except json.JSONDecodeError:
                        continue

                for entry in entries:
                    code = entry.get(code_key)
                    name = entry.get(name_key)
                    if code is not None and name:
                        self._lookup[(country_code, str(code))] = name
                        self._loaded_count += 1

        print(f"LocationMappingReader loaded {self._loaded_count} entries")

    def resolve(self, country_code: str, numeric_code) -> str | None:
        if country_code is None or numeric_code is None:
            return None
        return self._lookup.get((country_code.lower(), str(numeric_code)))