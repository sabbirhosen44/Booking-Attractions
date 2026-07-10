import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import ijson

from django.db import close_old_connections

from attractions.models import (
    AttractionLocalized,
    AttractionPhoto,
    AttractionReview,
    AttractionReviewScore,
)

from attractions.db_services import (
    AttractionDBService,
    ReviewDBService,
    ReviewScoreDBService,
)

from attractions.utils.attraction_row_builder import AttractionRowBuilder
from attractions.utils.batch_buffer import BatchBuffer
from attractions.utils.import_config import ImportConfig
from attractions.utils.locked_write import LockedWrite
from attractions.utils.skip_counter import SkipCounter


# Provides common functionality for all importers: file discovery, parallel execution and connection cleanup.
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

        with ThreadPoolExecutor(
            max_workers=self.config.MAX_WORKERS
        ) as executor:
            list(executor.map(self.process_file, files))

    @abstractmethod
    def process_file(self, file_path):
        raise NotImplementedError

    @staticmethod
    def close_connection():
        close_old_connections()

# Imports attraction details, localized content and photos
class AttractionDetailsImporter(BaseImporter):

    folder_name = "attraction_details"

    def __init__(self, config=ImportConfig):
        super().__init__(config)
        self.row_builder = AttractionRowBuilder()

    def _flush(self, attractions, localized, photos):
        with LockedWrite():
            if attractions:
                AttractionDBService.save_attractions(attractions.items())

            if localized:
                AttractionDBService.save_localized(localized.items())

            if photos:
                AttractionDBService.save_photos(photos.items())

        attractions.clear()
        localized.clear()
        photos.clear()

    def process_file(self, file_path):
        attractions = BatchBuffer(self.config.BATCH_SIZE)
        localized = BatchBuffer(self.config.BATCH_SIZE)
        photos = BatchBuffer(self.config.BATCH_SIZE)

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(f, "item"):

                    attractions.add(self.row_builder.build(item))

                    for lang, name in item.get("name", {}).items():
                        localized.add(
                            AttractionLocalized(
                                attraction_id=item["id"],
                                language_code=lang,
                                name=name,
                                description=item.get(
                                    "long_description", {}
                                ).get(lang),
                            )
                        )

                    for photo in item.get("photos", []):
                        photos.add(
                            AttractionPhoto(
                                attraction_id=item["id"],
                                photo_url=photo["url"],
                            )
                        )

                    if attractions.is_full():
                        self._flush(
                            attractions,
                            localized,
                            photos,
                        )

            if attractions or localized or photos:
                self._flush(
                    attractions,
                    localized,
                    photos,
                )

        finally:
            self.close_connection()


# Imports attraction reviews and skips reviews 
class ReviewsImporter(BaseImporter):

    folder_name = "reviews"

    def __init__(self, config=ImportConfig):
        super().__init__(config)
        self.existing_attractions = set()
        self.skip_counter = SkipCounter()

    def _load_existing_attraction_ids(self):
        return AttractionDBService.get_existing_attraction_ids()

    def _build_review_row(
        self,
        item,
        attraction_id,
    ):
        review_date = None

        if item.get("date"):
            review_date = (
                datetime.fromisoformat(
                    item["date"]
                ).date()
            )

        return AttractionReview(
            id=item["id"],
            attraction_id=attraction_id,
            author_name=item.get("author"),
            author_country_code=item.get(
                "author_country_code"
            ),
            rating=item.get("rating"),
            review_text=item.get("text"),
            language_code=item.get("language"),
            review_date=review_date,
        )

    def _flush(self, batch):
        with LockedWrite():
            ReviewDBService.save_reviews(batch.items())

        batch.clear()

    def process_file(self, file_path):
        batch = BatchBuffer(
            self.config.BATCH_SIZE
        )

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(
                    f,
                    "item",
                ):

                    attraction_id = item.get(
                        "attraction"
                    )

                    if (
                        attraction_id
                        not in self.existing_attractions
                    ):
                        self.skip_counter.increment()

                        print(
                            f"Skipping review "
                            f"{item.get('id')} "
                            f"-> missing attraction "
                            f"{attraction_id}"
                        )

                        continue

                    batch.add(
                        self._build_review_row(
                            item,
                            attraction_id,
                        )
                    )

                    if batch.is_full():
                        count = len(batch)
                        self._flush(batch)

                        print(
                            f"Inserted {count} reviews"
                        )

            if batch:
                count = len(batch)
                self._flush(batch)

                print(
                    f"Inserted final "
                    f"{count} reviews"
                )

        finally:
            self.close_connection()

    def run(self):
        print("Loading attraction ids...")

        self.existing_attractions = (
            self._load_existing_attraction_ids()
        )

        print(
            f"Loaded "
            f"{len(self.existing_attractions)} "
            f"attractions"
        )

        super().run()

        print(
            f"\nSkipped reviews: "
            f"{self.skip_counter.total}"
        )


# Imports review score breakdowns for attractions.
class ReviewScoresImporter(BaseImporter):

    folder_name = "reviews_scores"

    def _flush(self, batch):
        with LockedWrite():
            ReviewScoreDBService.save_scores(batch.items())

        batch.clear()

    def process_file(self, file_path):
        batch = BatchBuffer(
            self.config.BATCH_SIZE
        )

        try:
            print(f"Processing {file_path}")

            with open(file_path, "rb") as f:
                for item in ijson.items(
                    f,
                    "item",
                ):

                    attraction_id = item["id"]

                    for (
                        score_type,
                        score_data,
                    ) in item.get(
                        "breakdown",
                        {},
                    ).items():

                        batch.add(
                            AttractionReviewScore(
                                attraction_id=attraction_id,
                                score_type=score_type,
                                score=score_data.get(
                                    "score"
                                ),
                                review_count=score_data.get(
                                    "number_of_reviews"
                                ),
                            )
                        )

                    if batch.is_full():
                        self._flush(batch)

            if batch:
                self._flush(batch)

        finally:
            self.close_connection()


# Coordinates execution of all importers and reports the total import duration.
class DataImportRunner:

    importer_classes = [
        AttractionDetailsImporter,
        ReviewsImporter,
        ReviewScoresImporter,
    ]

    def __init__(
        self,
        config=ImportConfig,
    ):
        self.config = config

    def run(self):
        start = time.time()

        for importer_class in self.importer_classes:
            importer_class(
                self.config
            ).run()

        print(
            f"Completed in "
            f"{time.time() - start:.2f} "
            f"seconds"
        )