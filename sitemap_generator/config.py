from pathlib import Path

from core.configuration import BASE_DIR, SITEMAP


# Sitemap generation settings
class SitemapConfig:
    SITE_URL = SITEMAP.get("site_url", "https://www.rentbyowner.com")
    OUTPUT_DIR = Path(BASE_DIR) / SITEMAP.get("output_dir", "sitemap_output")
    GZIP_OUTPUT = SITEMAP.get("gzip_output", True)
    BATCH_SIZE = SITEMAP.get("batch_size", 1000)
    MAX_URLS_PER_FILE = SITEMAP.get("max_urls_per_file", 50000)
    MAX_FILE_SIZE_MB = SITEMAP.get("max_file_size_mb", 50)
    NEARBY_RADIUS_KM = SITEMAP.get("nearby_radius_km", 5)
