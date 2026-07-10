from attractions.models import Attraction

# Converts raw attraction JSON data into Attraction model instances.
class AttractionRowBuilder:
    @staticmethod
    def _select_arrival_location(item):
        locations = item.get("locations", [])
        return next(
            (
                loc
                for loc in locations
                if loc.get("type") == "arrival"
            ),
            {},
        )

    @classmethod
    def build(cls, item):
        location = cls._select_arrival_location(item)
        coordinates = location.get("coordinates", {})

        return Attraction(
            id=item["id"],
            duration=item.get("duration"),
            rating_score=item.get("ratings", {}).get("score"),
            rating_review_count=item.get("ratings", {}).get(
                "number_of_reviews"
            ),
            categories=item.get("categories", []),
            badges=item.get("badges", []),
            booking_web_url=item.get("urls", {})
            .get("web", {})
            .get("detail"),
            booking_app_url=item.get("urls", {})
            .get("app", {})
            .get("detail"),
            city_id=location.get("city"),
            country_code=location.get("country"),
            latitude=coordinates.get("latitude"),
            longitude=coordinates.get("longitude"),
            address=location.get("address"),
            post_code=location.get("post_code"),
            location_type=location.get("type"),
        )