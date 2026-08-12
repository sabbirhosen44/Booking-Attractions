class PropertyTransformer:

    def transform(self, property_data):
        return {
            "booking_id": self._value(property_data.get("booking_id")),
            "property_name": self._value(property_data.get("property_name")),
            "property_slug": self._value(property_data.get("property_slug")),
            "city": self._value(property_data.get("city")),
            "country_code": self._value(
                property_data.get("country_code")
            ).upper(),
            "property_type": "void",
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