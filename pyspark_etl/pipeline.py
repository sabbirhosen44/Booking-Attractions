import time

from pyspark.sql import functions as F

from pyspark_etl.config import SparkConfig
from pyspark_etl.session import get_spark_session
from pyspark_etl.catalog.align import align_to_schema
from pyspark_etl.schemas.source import (
    ATTRACTION_DETAILS_SCHEMA,
    REVIEWS_SCHEMA,
    REVIEWS_SCORES_SCHEMA,
    SEARCH_SCHEMA,
)
from pyspark_etl.readers.json_reader import read_json_folder
from pyspark_etl.readers.location_mapping_reader import read_location_mapping
from pyspark_etl.transforms.rental_property import build_rental_property_frames
from pyspark_etl.transforms.property_reviews import build_property_reviews_frames
from pyspark_etl.transforms.price_history import build_price_history_frames

from pyspark_etl.services import (
    IcebergAttractionDBService,
    IcebergPriceHistoryDBService,
    IcebergReviewDBService,
    IcebergReviewScoreDBService,
    IcebergSkipPropertiesDBService,
)

EMPTY_LOOKUP_SCHEMA = "country_code STRING, code STRING, name STRING"


# Runs the attraction_details -> reviews -> reviews_scores -> search pipeline against Iceberg
class IcebergDataImportRunner:

    def run(self):
        start = time.time()
        spark = get_spark_session()

        try:
            IcebergAttractionDBService.ensure_tables(spark)

            location_lookup = read_location_mapping(spark, SparkConfig.DATA_DIR)
            if location_lookup is None:
                location_lookup = spark.createDataFrame([], EMPTY_LOOKUP_SCHEMA)

            print("Processing attraction_details...")
            details_df = read_json_folder(
                spark, SparkConfig.DATA_DIR / "attraction_details", ATTRACTION_DETAILS_SCHEMA
            )
            property_df, localize_df, image_df = build_rental_property_frames(
                details_df, location_lookup
            )
            IcebergAttractionDBService.save_properties(
                spark, align_to_schema(property_df, "rental_property")
            )
            IcebergAttractionDBService.save_localized(
                spark, align_to_schema(localize_df, "rental_property_localize")
            )
            IcebergAttractionDBService.save_photos(
                align_to_schema(image_df, "property_image_meta")
            )
            print(f"Imported {property_df.count()} attractions")

            known_ids = IcebergAttractionDBService.get_existing_attraction_ids(spark)

            print("Processing reviews...")
            reviews_df = read_json_folder(spark, SparkConfig.DATA_DIR / "reviews", REVIEWS_SCHEMA)
            reviews_out, review_skips = build_property_reviews_frames(reviews_df, known_ids)
            IcebergReviewDBService.save_reviews(
                spark, align_to_schema(reviews_out, "property_reviews")
            )
            IcebergSkipPropertiesDBService.save_skips(
                spark, align_to_schema(review_skips, "skip_properties")
            )
            print(f"Inserted {reviews_out.count()} reviews, skipped {review_skips.count()}")

            print("Processing reviews_scores...")
            scores_df = read_json_folder(
                spark, SparkConfig.DATA_DIR / "reviews_scores", REVIEWS_SCORES_SCHEMA
            )
            scores_updates = scores_df.select(
                F.col("id"), F.to_json(F.col("breakdown")).alias("review_scores")
            )
            IcebergReviewScoreDBService.save_scores(spark, scores_updates)
            print(f"Updated review scores for {scores_updates.count()} attractions")

            print("Processing search...")
            search_df = read_json_folder(spark, SparkConfig.DATA_DIR / "search", SEARCH_SCHEMA)
            price_out, price_skips, pricing_updates, date_updates = build_price_history_frames(
                search_df, known_ids
            )
            IcebergPriceHistoryDBService.save_prices(
                align_to_schema(price_out, "price_history")
            )
            IcebergSkipPropertiesDBService.save_skips(
                spark, align_to_schema(price_skips, "skip_properties")
            )
            IcebergAttractionDBService.update_pricing(spark, pricing_updates)
            IcebergAttractionDBService.update_dates(spark, date_updates)
            print(f"Inserted {price_out.count()} price snapshots, skipped {price_skips.count()}")

        finally:
            spark.stop()

        print(f"Completed in {time.time() - start:.2f} seconds")
