from pathlib import Path

from core.configuration import BASE_DIR, SITEMAP


# Sitemap generation settings
class SitemapConfig:
    SITE_URL = SITEMAP.get("site_url", "https://www.rentbyowner.com")
    OUTPUT_DIR = Path(BASE_DIR) / SITEMAP.get("output_dir", "sitemap_output")
    GZIP_OUTPUT = SITEMAP.get("gzip_output", True)
