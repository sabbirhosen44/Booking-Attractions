from xml.sax.saxutils import escape

from sitemap_generator.url_builder import UrlBuilder

NAMESPACES = (
    'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
    'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" '
    'xmlns:xhtml="http://www.w3.org/1999/xhtml"'
)


# Builds one <url> block per (country_code, city) pair.
# No state-level page - state is null on every row in this dataset.
# No multi-domain hreflang alternates - this project has one domain.
class CitySitemapBuilder:
    @staticmethod
    def build_url_block(country_code: str, city: str, sample_image: str | None) -> str:
        loc = escape(UrlBuilder.city_url(country_code, city))
        image_block = (
            f"<image:image><image:loc>{escape(sample_image)}</image:loc></image:image>"
            if sample_image else ""
        )

        return (
            "<url>"
            f"<loc>{loc}</loc>"
            f'<xhtml:link rel="alternate" hreflang="en" href="{loc}"/>'
            f"{image_block}"
            "</url>"
        )

    @classmethod
    def build_urlset(cls, city_groups: list) -> str:
        blocks = "".join(
            cls.build_url_block(g["country_code"], g["city"], g.get("sample_image"))
            for g in city_groups
        )
        return (
            "<?xml version='1.0' encoding='utf-8'?>\n"
            f"<urlset {NAMESPACES}>{blocks}</urlset>"
        )
