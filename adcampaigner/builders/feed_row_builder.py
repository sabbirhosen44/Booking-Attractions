from adcampaigner.utils.normalizer import ValueNormalizer

class FeedRowBuilder:

    def build(self, page_url, custom_label):
        return {
            "page_url": ValueNormalizer.normalize(page_url),
            "custom_label": ValueNormalizer.normalize(custom_label),
        }

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return str(value)