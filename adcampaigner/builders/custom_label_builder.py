class CustomLabelBuilder:

    FIELD_SEPARATOR = ";"

    def build(
        self,
        city,
        country,
        property_type,
        price_segment,
        price,
        property_score,
        continent,
        tier,
        region,
    ):
        fields = [
            "SINGLE_PRODUCT",
            self._value(city),
            self._value(country),
            self._value(property_type),
            self._value(price_segment),
            self._number_value(price),
            self._number_value(property_score),
            "void",
            "BOOKING.COM",
            self._value(continent),
            self._value(tier),
            "property",
            self._value(region),
        ]

        return self.FIELD_SEPARATOR.join(fields)

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return str(value)

    def _number_value(self, value):
        if value is None:
            return "void"

        try:
            number = float(value)
        except (TypeError, ValueError):
            return "void"

        if number.is_integer():
            return str(int(number))

        return str(number)