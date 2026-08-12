class FeedRowBuilder:

    def build(self, page_url, custom_label):
        return {
            "page_url": self._value(page_url),
            "custom_label": self._value(custom_label),
        }

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return str(value)