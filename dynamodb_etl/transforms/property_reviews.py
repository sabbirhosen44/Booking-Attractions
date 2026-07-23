from datetime import datetime, timezone


# Builds review items, reviews use "attraction" not "attraction_id"
class PropertyReviewsTransform:
    @staticmethod
    def build_item(record: dict) -> dict:
        reviewer = record.get("reviewer") or {}
        return {
            "id": record.get("id"),
            "property_id": record.get("attraction"),
            "feed": "111",
            "country_code": (reviewer.get("country") or "xx").lower()[:2],
            "language_code": record.get("language_code", "en"),
            "score": record.get("score", 0),
            "summary": record.get("summary"),
            "negative": record.get("negative"),
            "positive": record.get("positive"),
            "reviewer": reviewer,
            "review_date": record.get("review_date"),
            "checkin_date": record.get("checkin_date"),
            "checkout_date": record.get("checkout_date"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def build_skip_item(record: dict, reason: str) -> dict:
        return {
            "property_id": record.get("attraction"),
            "feed": "111",
            "reason": reason,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "updated_by": "import_attractions_dynamodb",
        }
