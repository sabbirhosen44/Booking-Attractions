from xml.sax.saxutils import escape

from sitemap_generator.url_builder import UrlBuilder

NAMESPACES = (
    'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml"'
)

# Builds XML sitemap for property rows
class PropertySitemapBuilder:
    @staticmethod
    def build_url_block(row: dict) -> str:
        loc = escape(
            UrlBuilder.property_url(
                row["id"],
                row["property_slug"],
            )
        )

        lastmod = row["updated_at"].isoformat()

        images = row.get("images") or []

        image_blocks = "".join(
            (
                "<image:image>"
                f"<image:loc>{escape(image)}</image:loc>"
                "</image:image>"
            )
            for image in images
        )

        return (
            "<url>"
            f"<loc>{loc}</loc>"
            f'<xhtml:link rel="alternate" hreflang="en" href="{loc}"/>'
            f"<lastmod>{lastmod}</lastmod>"
            f"{image_blocks}"
            "</url>"
        )

    @classmethod
    def build_urlset(cls, rows: list[dict]) -> str:
        url_blocks = "".join(
            cls.build_url_block(row)
            for row in rows
        )

        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            f"<urlset {NAMESPACES}>"
            f"{url_blocks}"
            "</urlset>"
        )