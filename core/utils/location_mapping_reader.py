import json
from pathlib import Path
from typing import Dict, Tuple


# Resolves numeric location codes to names, city > district > landmark > region
class LocationMappingReader:
    PRIORITY_FILES = ("city.json", "district.json", "landmark.json", "region.json")

    def __init__(self, static_dir: Path):
        self._lookup: Dict[Tuple[str, str], str] = {}
        self._load(static_dir / "location_mapping")

    def _load(self, mapping_root: Path) -> None:
        if not mapping_root.exists():
            return

        for country_dir in mapping_root.iterdir():
            if not country_dir.is_dir():
                continue
            country_code = country_dir.name.lower()

            for filename in reversed(self.PRIORITY_FILES):
                file_path = country_dir / filename
                if not file_path.exists():
                    continue
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        entries = json.load(f)
                    except json.JSONDecodeError:
                        continue

                for entry in entries:
                    code = str(entry.get("id") or entry.get("code") or "")
                    name = entry.get("name")
                    if code and name:
                        self._lookup[(country_code, code)] = name

    def resolve(self, country_code: str, numeric_code) -> str | None:
        if country_code is None or numeric_code is None:
            return None
        return self._lookup.get((country_code.lower(), str(numeric_code)))
