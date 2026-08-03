from sitemap_generator.config import SitemapConfig


# Builds the actual URLs used in the sitemap
class UrlBuilder:
    @staticmethod
    def property_url(property_id: str, property_slug: str) -> str:
        return f"{SitemapConfig.SITE_URL}/property/{property_slug}/{property_id}"

