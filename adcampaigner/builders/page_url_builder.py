from urllib.parse import quote

from adcampaigner.config import AdCampaignerConfig


class PageUrlBuilder:

    def __init__(self, site_url=None):
        self.site_url = (
            site_url or AdCampaignerConfig.SITE_URL
        ).rstrip("/")

    def build(self, property_data):
        slug = self._value(
            property_data.get("property_slug")
        )

        property_id = self._get_property_id(
            property_data
        )

        if slug == "void" or property_id == "void":
            return "void"

        return (
            f"{self.site_url}/"
            f"{AdCampaignerConfig.ROUTE}/"
            f"{quote(slug, safe='')}/"
            f"{quote(property_id, safe='')}"
        )

    def _get_property_id(self, property_data):
        booking_id = property_data.get("booking_id")

        if booking_id:
            return self._value(booking_id)

        property_id = property_data.get("id")

        return self._value(property_id)

    def _value(self, value):
        if value is None:
            return "void"

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return "void"

        return str(value)