from pathlib import Path

from core.configuration import ADCAMPAIGNER


# Loads configuration and prepares shared pipeline settings
class AdCampaignerConfig:

    BASE_DIR = Path(__file__).resolve().parent.parent

    OUTPUT_DIR = BASE_DIR / ADCAMPAIGNER.get(
        "output_dir",
        "adcampaigner/output",
    )

    MAX_ROWS_PER_FILE = int(
        ADCAMPAIGNER.get("max_rows_per_file", 700000)
    )

    SITE_URL = ADCAMPAIGNER.get(
        "site_url",
        "https://www.rentbyowner.com",
    ).rstrip("/")

    FEED_BASE_URL = ADCAMPAIGNER.get(
        "feed_base_url",
        "https://cdn.rentbyowner.com/property-marketing-ads/google-page-feed/property/property-all",
    ).rstrip("/")
    
    REMARKETING_FEED_BASE_URL = ADCAMPAIGNER.get(
        "remarketing_feed_base_url",
        "https://cdn.rentbyowner.com/property-marketing-ads/google-re-marketing-feed/property-all",
    ).rstrip("/")

    PARTNER = ADCAMPAIGNER.get("partner", "BOOKING.COM")
    ROUTE = ADCAMPAIGNER.get("route", "property")
    LOCATION_NAMES = ADCAMPAIGNER.get("location_names", "all")
    STATUS = int(ADCAMPAIGNER.get("status", 202))

    COUNTRY_MAP_FILE = BASE_DIR / ADCAMPAIGNER.get(
        "country_map_file",
        "data/country_map.json",
    )

    TIER_REGION_CONTINENT_MAP_FILE = BASE_DIR / ADCAMPAIGNER.get(
        "tier_region_continent_map_file",
        "data/tier_region_continent_map.json",
    )

    PRICE_SCORE_PERCENTILES_FILE = BASE_DIR / ADCAMPAIGNER.get(
        "price_score_percentiles_file",
        "data/price_score_percentiles.json",
    )

    PROPERTY_TYPE = "void"
    CATEGORY_ATTRIBUTE = "void"

    LABEL_SOURCE = "BOOKING.COM"
    LABEL_ROUTE = "property"

    FILE_PREFIX = "rbo_google_page_property_feed_booking"
    
    REMARKETING_FILE_PREFIX = "rbo_google_re-marketing_property_feed_booking"
    
    REMARKETING_ORIGIN_PARAM = "csv_feed"
    
    STAR_RATING_VALUE = "void"
    
    PAGE_CAMPAIGN_TYPE = "page_feed"
    
    REMARKETING_CAMPAIGN_TYPE = "re-marketing_feed"

    INDEX_FILE_NAME = "index.html"

    CONTINENT_CODES = (
        "africa",
        "as",
        "eu",
        "nam",
        "oc",
        "sam",
    )

    @classmethod
    def get_continent_file_name(
        cls,
        continent_code: str,
        part: int = 1,
    ) -> str:
        if part == 1:
            return f"{cls.FILE_PREFIX}_{continent_code}.csv"

        return f"{cls.FILE_PREFIX}_{continent_code}_part{part}.csv"

    @classmethod
    def get_remarketing_file_name(cls, part: int = 1) -> str:
        return f"{cls.REMARKETING_FILE_PREFIX}_part{part}.csv"

    @classmethod
    def get_remarketing_feed_url(cls, filename: str) -> str:
        return f"{cls.REMARKETING_FEED_BASE_URL}/{filename}"

    @classmethod
    def get_feed_url(cls, filename: str) -> str:
        return f"{cls.FEED_BASE_URL}/{filename}"

    @classmethod
    def ensure_output_directory(cls) -> None:
        cls.OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    @classmethod
    def validate(cls) -> None:
        required_files = {
            "country_map_file": cls.COUNTRY_MAP_FILE,
            "tier_region_continent_map_file": (
                cls.TIER_REGION_CONTINENT_MAP_FILE
            ),
            "price_score_percentiles_file": (
                cls.PRICE_SCORE_PERCENTILES_FILE
            ),
        }

        if cls.MAX_ROWS_PER_FILE <= 0:
            raise ValueError(
                "max_rows_per_file must be greater than zero."
            )

        missing_files = [
            f"{name}: {path}"
            for name, path in required_files.items()
            if not path.exists()
        ]

        if missing_files:
            details = "\n".join(
                f"- {item}"
                for item in missing_files
            )

            raise FileNotFoundError(
                "Missing AdCampaigner data files:\n"
                f"{details}"
            )

        cls.ensure_output_directory()