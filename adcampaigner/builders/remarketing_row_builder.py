from urllib.parse import urlencode


class RemarketingRowBuilder:

    ORIGIN_PARAM = "csv_feed"

    OPENERS = [
        "Discover",
        "Explore",
        "Enjoy",
        "Experience",
        "Book",
    ]

    def build(self, property_data, location, page_url, property_score):
        if page_url == "void":
            return None

        return {
            "property_id": property_data.get("booking_id"),
            "property_name": property_data.get("property_name"),
            "final_url": self._final_url(page_url, property_score),
            "image_url": property_data.get("image_url"),
            "destination_name": self._destination_name(
                property_data, location
            ),
            "description": self._description(property_data, location),
            "price": self._price(property_data.get("usd_price")),
            "star_rating": "void",
            "category": property_data.get("category"),
        }

    def _final_url(self, page_url, property_score):
        params = {
            "origin": self.ORIGIN_PARAM,
            "score": self._score_value(property_score),
        }

        return f"{page_url}?{urlencode(params)}"

    def _score_value(self, property_score):
        if property_score is None or property_score == "void":
            return "void"

        return property_score

    def _destination_name(self, property_data, location):
        city = self._value(property_data.get("city"))
        state = self._value(property_data.get("state"))
        country = self._value(location.get("country"))

        return f"{city}, {state}, {country}"

    def _description(self, property_data, location):
        category_phrase = self._humanize(
            property_data.get("category")
        )

        city = property_data.get("city")
        country = location.get("country")
        location_phrase = self._location_phrase(city, country)

        opener = self._opener(property_data.get("booking_id"))

        if location_phrase:
            return f"{opener} this {category_phrase} in {location_phrase}."

        return f"{opener} this {category_phrase} experience."

    def _opener(self, booking_id):
        if not booking_id:
            return self.OPENERS[0]

        index = sum(ord(char) for char in str(booking_id)) % len(
            self.OPENERS
        )

        return self.OPENERS[index]

    def _location_phrase(self, city, country):
        city = city if city and city != "void" else None
        country = country if country and country != "void" else None

        if city and country:
            return f"{city}, {country}"

        return city or country or ""

    @staticmethod
    def _humanize(value):
        if not value or value == "void":
            return "experience"

        return str(value).replace("_", " ").strip().lower()

    def _price(self, value):
        if value is None:
            return "void"

        try:
            return f"{int(round(float(value)))} USD"
        except (TypeError, ValueError):
            return "void"

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return str(value)