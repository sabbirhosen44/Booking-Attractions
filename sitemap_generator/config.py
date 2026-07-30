from pathlib import Path

from core.configuration import BASE_DIR, SITEMAP


# Sitemap generation settings
class SitemapConfig:
    SITE_URL = SITEMAP.get("site_url", "https://www.rentbyowner.com")
    OUTPUT_DIR = Path(BASE_DIR) / SITEMAP.get("output_dir", "sitemap_output")
    IMAGES_PER_PROPERTY = SITEMAP.get("images_per_property", 5)
    URLS_PER_FILE = SITEMAP.get("urls_per_file", 50000)
    GZIP_OUTPUT = SITEMAP.get("gzip_output", True)
