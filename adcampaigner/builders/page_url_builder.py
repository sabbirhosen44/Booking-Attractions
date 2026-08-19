from urllib.parse import quote

from adcampaigner.config import AdCampaignerConfig
from adcampaigner.utils.normalizer import ValueNormalizer


class PageUrlBuilder:

    def __init__(self, site_url=None):
        self.site_url = (
            site_url or AdCampaignerConfig.SITE_URL
        ).rstrip("/")

    def build(self, property_data):
        slug = ValueNormalizer.normalize(
            property_data.get("property_slug")
        )

        property_id = self._get_property_id(property_data)

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
            return ValueNormalizer.normalize(booking_id)

        return ValueNormalizer.normalize(
            property_data.get("id")
        )