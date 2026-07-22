from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs


# Builds price docs, dates come from url query params
class PriceHistoryTransform:
    @staticmethod
    def _extract_dates(url: str) -> tuple:
        if not url:
            return None, None
        query = parse_qs(urlparse(url).query)
        start = query.get("start_date", [None])[0]
        end = query.get("end_date", [None])[0]
        return start, end

    @classmethod
    def build_doc(cls, record: dict) -> dict:
        urls = record.get("urls") or {}
        booking_url = (urls.get("web") or {}).get("detail") or urls.get("detail")
        start_date, end_date = cls._extract_dates(booking_url)

        return {
            "property_id": record.get("attraction") or record.get("attraction_id"),
            "price": record.get("price"),
            "check_in": start_date,
            "check_out": end_date,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "feed": "111",
            "country_code": (record.get("country_code") or "xx").lower(),
        }

    @staticmethod
    def build_skip_doc(record: dict, reason: str) -> dict:
        return {
            "property_id": record.get("attraction") or record.get("attraction_id"),
            "feed": "111",
            "reason": reason,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "import_attractions_elasticsearch",
        }
