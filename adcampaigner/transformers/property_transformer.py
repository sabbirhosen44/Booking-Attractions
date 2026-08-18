class PropertyTransformer:

    def transform(self, property_data):
        return {
            "booking_id": self._value(property_data.get("booking_id")),
            "property_name": self._value(property_data.get("property_name")),
            "property_slug": self._value(property_data.get("property_slug")),
            "city": self._value(property_data.get("city")),
            "state": self._value(property_data.get("state")),
            "country_code": self._value(
                property_data.get("country_code")
            ).upper(),
            "property_type": "void",
            "category": self._first_category(property_data),
            "image_url": self._first_image(property_data),
            "property_attributes": self._attributes_list(property_data),
            "usd_price": self._price(
                property_data.get("usd_price")
            ),
        }

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return value

    def _price(self, value):
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _first_category(self, property_data):
        categories = property_data.get("activity_categories")

        if not categories:
            return "void"

        for category in categories:
            if category and str(category).strip():
                return str(category).strip()

        return "void"

    def _first_image(self, property_data):
        images = property_data.get("images")

        if not images:
            return "void"

        for image in images:
            if image and str(image).strip():
                return str(image).strip()

        return "void"

    def _attributes_list(self, property_data):
        attributes = property_data.get("property_attributes")

        if not attributes:
            return []

        return [
            str(attr).strip()
            for attr in attributes
            if attr and str(attr).strip()
        ]