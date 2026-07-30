from datetime import datetime, timezone
from xml.sax.saxutils import escape

from sitemap_generator.config import SitemapConfig


# Builds the master index listing every generated sitemap file
class SitemapIndexBuilder:
    @staticmethod
    def build(filenames: list) -> str:
        now = datetime.now(timezone.utc).isoformat()
        extension = ".xml.gz" if SitemapConfig.GZIP_OUTPUT else ".xml"

        entries = "".join(
            "<sitemap>"
            f"<loc>{escape(SitemapConfig.SITE_URL)}/sitemap/{name}{extension}</loc>"
            f"<lastmod>{now}</lastmod>"
            "</sitemap>"
            for name in filenames
        )

        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{entries}"
            "</sitemapindex>"
        )
