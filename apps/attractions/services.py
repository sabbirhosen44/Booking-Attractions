import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import ijson

from django.db import close_old_connections

from apps.attractions.db_services import (
    AttractionDBService,
    PriceHistoryDBService,
    ReviewDBService,
    ReviewScoreDBService,
    SkipPropertiesDBService,
)

from core.utils.batch_buffer import BatchBuffer
from core.utils.locked_write import LockedWrite
from core.utils.import_config import ImportConfig
from core.utils.attraction_row_builder import AttractionRowBuilder
from core.utils.price_row_builder import PriceRowBuilder
from core.utils.review_row_builder import ReviewRowBuilder
from core.utils.skip_counter import SkipCounter


# Base class shared by all importers: file discovery, threading, connection cleanup
class BaseImporter(ABC):

    folder_name = None

    def __init__(self, config=ImportConfig):
        self.config = config

    def get_files(self):
        folder = self.config.DATA_DIR / self.folder_name
        return list(folder.rglob("*.json"))

    def run(self):
        files = self.get_files()

        if not files:
            print(f"No files found in {self.folder_name}")
            return

        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            list(executor.map(self.process_file, files))

    @abstractmethod
    def process_file(self, file_path):
        raise NotImplementedError

    @staticmethod
    def close_connection():
        close_old_connections()


# Imports attraction details into RentalProperty, RentalPropertyLocalize and PropertyImageMeta
class AttractionDetailsImporter(BaseImporter):

    folder_name = "attraction_details"

    def __init__(self, config=ImportConfig):
        super().__init__(config)
        self.row_builder = AttractionRowBuilder()

    def _flush(self, properties, localized, photos):
        with LockedWrite():
            if properties:
                AttractionDBService.save_properties(properties.items())

            if localized:
                AttractionDBService.save_localized(localized.items())

            if photos:
                AttractionDBService.save_photos(photos.items())

        properties.clear()
        localized.clear()
        photos.clear()

    def process_file(self, file_path):
        properties = BatchBuffer(self.config.BATCH_SIZE)
        localized = BatchBuffer(self.config.BATCH_SIZE)
        photos = BatchBuffer(self.config.BATCH_SIZE)

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(f, "item", use_float=True):

                    property_row, localized_rows, photo_rows = (
                        self.row_builder.build(item)
                    )

                    properties.add(property_row)

                    for row in localized_rows:
                        localized.add(row)

                    for row in photo_rows:
                        photos.add(row)

                    if properties.is_full():
                        self._flush(properties, localized, photos)

            if properties or localized or photos:
                self._flush(properties, localized, photos)

        finally:
            self.close_connection()


# Imports attraction reviews into PropertyReviews, skipping ones with no matching attraction
class ReviewsImporter(BaseImporter):

    folder_name = "reviews"

    def __init__(self, config=ImportConfig):
        super().__init__(config)
        self.attraction_country_map = {}
        self.skip_counter = SkipCounter()
        self.row_builder = ReviewRowBuilder()

    def _load_attraction_country_map(self):
        return AttractionDBService.get_existing_attraction_country_map()

    def _flush(self, batch, skips):
        with LockedWrite():
            ReviewDBService.save_reviews(batch.items())

            if skips:
                SkipPropertiesDBService.save_skips(skips.items())

        batch.clear()
        skips.clear()

    def process_file(self, file_path):
        batch = BatchBuffer(self.config.BATCH_SIZE)
        skips = BatchBuffer(self.config.BATCH_SIZE)

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(f, "item", use_float=True):

                    attraction_id = item.get("attraction")

                    if attraction_id not in self.attraction_country_map:
                        self.skip_counter.increment()

                        skips.add(
                            {
                                "property_id": attraction_id,
                                "reason": (
                                    f"review {item.get('id')} references "
                                    f"an attraction not yet imported"
                                ),
                            }
                        )

                        print(
                            f"Skipping review {item.get('id')} "
                            f"-> missing attraction {attraction_id}"
                        )

                        continue

                    country_code = self.attraction_country_map[attraction_id]

                    batch.add(
                        self.row_builder.build(item, attraction_id, country_code)
                    )

                    if batch.is_full():
                        count = len(batch)
                        self._flush(batch, skips)
                        print(f"Inserted {count} reviews")

            if batch or skips:
                count = len(batch)
                self._flush(batch, skips)
                print(f"Inserted final {count} reviews")

        finally:
            self.close_connection()

    def run(self):
        print("Loading attraction country map...")
        self.attraction_country_map = self._load_attraction_country_map()
        print(f"Loaded {len(self.attraction_country_map)} attractions")

        super().run()

        print(f"\nSkipped reviews: {self.skip_counter.total}")


# Folds review score breakdowns into RentalProperty.review_scores
class ReviewScoresImporter(BaseImporter):

    folder_name = "reviews_scores"

    def _flush(self, buffer):
        with LockedWrite():
            ReviewScoreDBService.save_scores(dict(buffer))

        buffer.clear()

    def process_file(self, file_path):
        buffer = {}

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(f, "item", use_float=True):
                    attraction_id = item["id"]
                    buffer[attraction_id] = item.get("breakdown", {})

                    if len(buffer) >= self.config.BATCH_SIZE:
                        self._flush(buffer)

            if buffer:
                self._flush(buffer)

        finally:
            self.close_connection()


# Imports search/price snapshots into PriceHistory and refreshes RentalProperty pricing
class SearchImporter(BaseImporter):

    folder_name = "search"

    def __init__(self, config=ImportConfig):
        super().__init__(config)
        self.attraction_country_map = {}
        self.skip_counter = SkipCounter()
        self.row_builder = PriceRowBuilder()

    def _flush(self, prices, property_updates, date_updates, skips):
        with LockedWrite():
            if prices:
                PriceHistoryDBService.save_prices(prices.items())

            if property_updates:
                AttractionDBService.update_pricing(dict(property_updates))

            if date_updates:
                AttractionDBService.update_dates(dict(date_updates))

            if skips:
                SkipPropertiesDBService.save_skips(skips.items())

        prices.clear()
        property_updates.clear()
        date_updates.clear()
        skips.clear()

    def process_file(self, file_path):
        prices = BatchBuffer(self.config.BATCH_SIZE)
        property_updates = {}
        date_updates = {}
        skips = BatchBuffer(self.config.BATCH_SIZE)

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(f, "item", use_float=True):

                    attraction_id = item["id"]

                    if attraction_id not in self.attraction_country_map:
                        self.skip_counter.increment()

                        skips.add(
                            {
                                "property_id": attraction_id,
                                "reason": (
                                    "price snapshot references an "
                                    "attraction not yet imported"
                                ),
                            }
                        )

                        print(f"Skipping price snapshot -> missing attraction {attraction_id}")
                        continue

                    country_code = self.attraction_country_map[attraction_id]

                    _, currency, total, price_row = self.row_builder.build(item, country_code)

                    prices.add(price_row)

                    if currency and total is not None:
                        property_updates[attraction_id] = (currency, total)

                    if price_row.get("check_in") or price_row.get("check_out"):
                        date_updates[attraction_id] = (
                            price_row.get("check_in"),
                            price_row.get("check_out"),
                        )

                    if prices.is_full():
                        self._flush(prices, property_updates, date_updates, skips)

            if prices or property_updates or date_updates or skips:
                self._flush(prices, property_updates, date_updates, skips)

        finally:
            self.close_connection()

    def run(self):
        print("Loading attraction country map...")
        self.attraction_country_map = AttractionDBService.get_existing_attraction_country_map()
        print(f"Loaded {len(self.attraction_country_map)} attractions")

        super().run()

        print(f"\nSkipped price snapshots: {self.skip_counter.total}")


# Runs all importers in order and reports total elapsed time
class DataImportRunner:

    importer_classes = [
        AttractionDetailsImporter,
        ReviewsImporter,
        ReviewScoresImporter,
        SearchImporter,
    ]

    def __init__(self, config=ImportConfig):
        self.config = config

    def run(self):
        start = time.time()

        for importer_class in self.importer_classes:
            importer_class(self.config).run()

        print(f"Completed in {time.time() - start:.2f} seconds")