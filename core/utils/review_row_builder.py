from datetime import datetime, timezone as dt_timezone

from apps.attractions.models import Feed


class ReviewRowBuilder:

    @staticmethod
    def _parse_date(value):
        if not value:
            return None

        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None

        if parsed.tzinfo is None:

            parsed = parsed.replace(tzinfo=dt_timezone.utc)

        return parsed

    def build(self, item, attraction_id, country_code):
        return {
            "id": item["id"],
            "property_id": attraction_id,
            "feed": Feed.BOOKING_ATTRACTION,
            "country_code": (country_code or "xx").lower(),
            "language_code": (item.get("language") or "en")[:3],
            "score": item.get("rating") or 0,
            "summary": item.get("text"),
            "reviewer": {
                "name": item.get("author"),
                "country": item.get("author_country_code"),
            },
            "review_date": self._parse_date(item.get("date")),
        }