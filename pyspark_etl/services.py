from pyspark_etl.config import SparkConfig
from pyspark_etl.catalog.tables import IcebergTableManager
from pyspark_etl.writers.iceberg_writer import IcebergWriter


# Saves attraction details, translations, photos, price updates
class IcebergAttractionDBService:

    @staticmethod
    def ensure_tables(spark):
        IcebergTableManager.ensure_tables(spark)

    @staticmethod
    def save_properties(spark, df):
        IcebergWriter.upsert(spark, df, SparkConfig.table("rental_property"), ["id"])

    @staticmethod
    def save_localized(spark, df):
        IcebergWriter.upsert(
            spark,
            df,
            SparkConfig.table("rental_property_localize"),
            ["property_id", "language", "country_code"],
        )

    @staticmethod
    def save_photos(df):
        IcebergWriter.append(df, SparkConfig.table("property_image_meta"))

    @staticmethod
    def get_existing_attraction_ids(spark):
        return spark.table(SparkConfig.table("rental_property")).select("id", "country_code")

    @staticmethod
    def update_pricing(spark, df):
        IcebergWriter.update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["currency", "usd_price"])

    @staticmethod
    def update_dates(spark, df):
        IcebergWriter.update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["check_in", "check_out"])


# Saves attraction reviews
class IcebergReviewDBService:

    @staticmethod
    def save_reviews(spark, df):
        IcebergWriter.upsert(spark, df, SparkConfig.table("property_reviews"), ["id"])


# Saves attraction review scores
class IcebergReviewScoreDBService:

    @staticmethod
    def save_scores(spark, df):
        IcebergWriter.update_columns(spark, df, SparkConfig.table("rental_property"), "id", ["review_scores"])


# Saves skipped attraction references
class IcebergSkipPropertiesDBService:

    @staticmethod
    def save_skips(spark, df):
        IcebergWriter.upsert(spark, df, SparkConfig.table("skip_properties"), ["property_id"])


# Saves attraction price history
class IcebergPriceHistoryDBService:

    @staticmethod
    def save_prices(df):
        IcebergWriter.append(df, SparkConfig.table("price_history"))
