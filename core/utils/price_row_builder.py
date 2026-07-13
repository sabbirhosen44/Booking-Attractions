from datetime import datetime
from urllib.parse import urlparse, parse_qs

from apps.attractions.models import Feed


# Builds PriceHistory rows (as plain dicts) from a raw Booking Attractions
class PriceRowBuilder:

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _extract_dates(self, urls):
        web_detail = (urls.get("web", {}) or {}).get("detail")

        if not web_detail:
            return None, None

        query = parse_qs(urlparse(web_detail).query)

        start = query.get("start_date", [None])[0]
        end = query.get("end_date", [None])[0]

        return self._parse_date(start), self._parse_date(end)

    def build(self, item, country_code):
        attraction_id = item["id"]
        price = item.get("price", {}) or {}
        urls = item.get("urls", {}) or {}

        check_in, check_out = self._extract_dates(urls)

        price_row = {
            "property_id": attraction_id,
            "feed": Feed.BOOKING_ATTRACTION,
            "price": price,
            "check_in": check_in,
            "check_out": check_out,
            "country_code": country_code,
        }

        return attraction_id, price.get("currency"), price.get("total"), price_row
