import time

from pyspark.sql import functions as F

from pyspark_etl.config import SparkConfig
from pyspark_etl.session import SparkSessionFactory
from pyspark_etl.catalog.align import SchemaAligner
from pyspark_etl.schemas.source import SourceSchemas
from pyspark_etl.readers.json_reader import JsonFolderReader
from pyspark_etl.readers.location_mapping_reader import LocationMappingReader
from pyspark_etl.transforms.rental_property import RentalPropertyTransform
from pyspark_etl.transforms.property_reviews import PropertyReviewsTransform
from pyspark_etl.transforms.price_history import PriceHistoryTransform

from pyspark_etl.services import (
    IcebergAttractionDBService,
    IcebergPriceHistoryDBService,
    IcebergReviewDBService,
    IcebergReviewScoreDBService,
    IcebergSkipPropertiesDBService,
)

EMPTY_LOOKUP_SCHEMA = "country_code STRING, code STRING, name STRING"


# Orchestrates the full attraction_details -> reviews -> search pipeline
class IcebergDataImportRunner:

    def run(self):
        start = time.time()
        spark = SparkSessionFactory.create()

        try:
            IcebergAttractionDBService.ensure_tables(spark)

            location_lookup = LocationMappingReader.read(spark, SparkConfig.DATA_DIR)
            if location_lookup is None:
                location_lookup = spark.createDataFrame([], EMPTY_LOOKUP_SCHEMA)

            print("Processing attraction_details...")
            details_df = JsonFolderReader.read(
                spark,
                SparkConfig.DATA_DIR / "attraction_details",
                SourceSchemas.ATTRACTION_DETAILS_SCHEMA,
            )
            property_df, localize_df, image_df = RentalPropertyTransform.build(
                details_df, location_lookup
            )
            IcebergAttractionDBService.save_properties(
                spark, SchemaAligner.align(property_df, "rental_property")
            )
            IcebergAttractionDBService.save_localized(
                spark, SchemaAligner.align(localize_df, "rental_property_localize")
            )
            IcebergAttractionDBService.save_photos(
                SchemaAligner.align(image_df, "property_image_meta")
            )
            print(f"Imported {property_df.count()} attractions")

            known_ids = IcebergAttractionDBService.get_existing_attraction_ids(spark)

            print("Processing reviews...")
            reviews_df = JsonFolderReader.read(
                spark, SparkConfig.DATA_DIR / "reviews", SourceSchemas.REVIEWS_SCHEMA
            )
            reviews_out, review_skips = PropertyReviewsTransform.build(reviews_df, known_ids)
            IcebergReviewDBService.save_reviews(
                spark, SchemaAligner.align(reviews_out, "property_reviews")
            )
            IcebergSkipPropertiesDBService.save_skips(
                spark, SchemaAligner.align(review_skips, "skip_properties")
            )
            print(f"Inserted {reviews_out.count()} reviews, skipped {review_skips.count()}")

            print("Processing reviews_scores...")
            scores_df = JsonFolderReader.read(
                spark, SparkConfig.DATA_DIR / "reviews_scores", SourceSchemas.REVIEWS_SCORES_SCHEMA
            )
            scores_updates = scores_df.select(
                F.col("id"), F.to_json(F.col("breakdown")).alias("review_scores")
            )
            IcebergReviewScoreDBService.save_scores(spark, scores_updates)
            print(f"Updated review scores for {scores_updates.count()} attractions")

            print("Processing search...")
            search_df = JsonFolderReader.read(
                spark, SparkConfig.DATA_DIR / "search", SourceSchemas.SEARCH_SCHEMA
            )
            price_out, price_skips, pricing_updates, date_updates = PriceHistoryTransform.build(
                search_df, known_ids
            )
            IcebergPriceHistoryDBService.save_prices(
                SchemaAligner.align(price_out, "price_history")
            )
            IcebergSkipPropertiesDBService.save_skips(
                spark, SchemaAligner.align(price_skips, "skip_properties")
            )
            IcebergAttractionDBService.update_pricing(spark, pricing_updates)
            IcebergAttractionDBService.update_dates(spark, date_updates)
            print(f"Inserted {price_out.count()} price snapshots, skipped {price_skips.count()}")

        finally:
            spark.stop()

        print(f"Completed in {time.time() - start:.2f} seconds")
