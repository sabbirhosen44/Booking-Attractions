from pyspark_etl.config import SparkConfig
from pyspark_etl.catalog.tables import ensure_tables
from pyspark_etl.writers.iceberg_writer import append, update_columns, upsert

# Handles saving attraction details, translations, photos and price/date updates in Iceberg
class IcebergAttractionDBService:

    @staticmethod
    def ensure_tables(spark):
        ensure_tables(spark)

    @staticmethod
    def save_properties(spark, df):
        upsert(spark, df, SparkConfig.table("rental_property"), ["id"])

    @staticmethod
    def save_localized(spark, df):
        upsert(
            spark,
            df,
            SparkConfig.table("rental_property_localize"),
            ["property_id", "language", "country_code"],
        )

    @staticmethod
    def save_photos(df):
        append(df, SparkConfig.table("property_image_meta"))

    @staticmethod
    def get_existing_attraction_ids(spark):
        return spark.table(SparkConfig.table("rental_property")).select("id", "country_code")

    @staticmethod
    def update_pricing(spark, df):
        update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["currency", "usd_price"])

    @staticmethod
    def update_dates(spark, df):
        update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["check_in", "check_out"])


# Handles saving attraction reviews in Iceberg
class IcebergReviewDBService:

    @staticmethod
    def save_reviews(spark, df):
        upsert(spark, df, SparkConfig.table("property_reviews"), ["id"])


# Handles saving attraction review scores in Iceberg
class IcebergReviewScoreDBService:

    @staticmethod
    def save_scores(spark, df):
        update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["review_scores"])


# Handles saving attractions that were skipped during import
class IcebergSkipPropertiesDBService:

    @staticmethod
    def save_skips(spark, df):
        upsert(spark, df, SparkConfig.table("skip_properties"), ["property_id"])


# Handles saving attraction price history in Iceberg
class IcebergPriceHistoryDBService:

    @staticmethod
    def save_prices(df):
        append(df, SparkConfig.table("price_history"))
