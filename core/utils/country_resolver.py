import json
import threading

from core.utils.import_config import ImportConfig


class CountryResolver:

    _FILE = "country.json"

    def __init__(self, config=ImportConfig):
        self.config = config
        self._mapping = None
        self._lock = threading.Lock()

    def _load(self):
        if self._mapping is not None:
            return self._mapping

        with self._lock:
            if self._mapping is not None:
                return self._mapping

            mapping = {}
            file_path = (
                self.config.DATA_DIR / "static" / "location_mapping" / self._FILE
            )

            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        entries = json.load(f)

                    for entry in entries:
                        code = entry.get("country_code")
                        name = entry.get("country")

                        if code is None or name is None:
                            continue

                        mapping[str(code).lower()] = name
                except (json.JSONDecodeError, OSError):
                    pass

            self._mapping = mapping
            return mapping

    def resolve(self, country_code):
        if not country_code:
            return None

        return self._load().get(str(country_code).lower())