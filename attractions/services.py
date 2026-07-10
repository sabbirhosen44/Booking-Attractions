import os
import time
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

import ijson

from django.conf import settings

from database import Base
from database import SessionLocal
from database import engine

from attractions.models import (
    Attraction,
    AttractionLocalized,
    AttractionPhoto,
    AttractionReview,
    AttractionReviewScore,
)

DATA_DIR = Path(settings.DATA_DIR)

BATCH_SIZE = 1000

# Number of worker threads used to read and parse files concurrently
MAX_WORKERS = min(8, os.cpu_count() or 4)

# Shared lock so only one thread writes to sqlite at a time
db_write_lock = threading.Lock()


# Create all database tables if they do not already exist
def create_tables():
    Base.metadata.create_all(bind=engine)


# Insert or update a batch of attraction rows
def flush_attractions(session, batch):
    if not batch:
        return

    stmt = insert(Attraction)
    stmt = stmt.values(batch)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "duration": stmt.excluded.duration,
            "rating_score": stmt.excluded.rating_score,
            "rating_review_count": stmt.excluded.rating_review_count,
            "categories": stmt.excluded.categories,
            "badges": stmt.excluded.badges,
            "booking_web_url": stmt.excluded.booking_web_url,
            "booking_app_url": stmt.excluded.booking_app_url,
            "city_id": stmt.excluded.city_id,
            "country_code": stmt.excluded.country_code,
            "latitude": stmt.excluded.latitude,
            "longitude": stmt.excluded.longitude,
            "address": stmt.excluded.address,
            "post_code": stmt.excluded.post_code,
            "location_type": stmt.excluded.location_type,
        },
    )

    session.execute(stmt)


# Insert or update a batch of localized attraction name/description rows
def flush_localized(session, batch):
    if not batch:
        return

    stmt = insert(AttractionLocalized)
    stmt = stmt.values(batch)
    stmt = stmt.on_conflict_do_update(
        index_elements=[
            "attraction_id",
            "language_code",
        ],
        set_={
            "name": stmt.excluded.name,
            "description": stmt.excluded.description,
        },
    )

    session.execute(stmt)


# Insert a batch of attraction photo rows, ignoring duplicates
def flush_photos(session, batch):
    if not batch:
        return

    stmt = insert(AttractionPhoto)
    stmt = stmt.values(batch)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=[
            "attraction_id",
            "photo_url",
        ]
    )

    session.execute(stmt)


# Insert or update a batch of attraction review rows
def flush_reviews(session, batch):
    if not batch:
        return

    stmt = insert(AttractionReview)
    stmt = stmt.values(batch)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "author_name": stmt.excluded.author_name,
            "author_country_code": stmt.excluded.author_country_code,
            "rating": stmt.excluded.rating,
            "review_text": stmt.excluded.review_text,
            "language_code": stmt.excluded.language_code,
            "review_date": stmt.excluded.review_date,
        },
    )

    session.execute(stmt)


# Insert or update a batch of attraction review score rows
def flush_review_scores(session, batch):
    if not batch:
        return

    stmt = insert(AttractionReviewScore)
    stmt = stmt.values(batch)
    stmt = stmt.on_conflict_do_update(
        index_elements=[
            "attraction_id",
            "score_type",
        ],
        set_={
            "score": stmt.excluded.score,
            "review_count": stmt.excluded.review_count,
        },
    )

    session.execute(stmt)


# Build the flat attraction dict from a raw json item
def _build_attraction_row(item):
    # Only the arrival location is relevant, other types (e.g. departure) are ignored
    locations = item.get("locations", [])
    location = next(
        (loc for loc in locations if loc.get("type") == "arrival"),
        {},
    )

    coordinates = location.get("coordinates", {})

    return {
        "id": item["id"],
        "duration": item.get("duration"),
        "rating_score": item.get("ratings", {}).get("score"),
        "rating_review_count": item.get("ratings", {}).get(
            "number_of_reviews"
        ),
        "categories": item.get("categories", []),
        "badges": item.get("badges", []),
        "booking_web_url": item.get("urls", {})
        .get("web", {})
        .get("detail"),
        "booking_app_url": item.get("urls", {})
        .get("app", {})
        .get("detail"),
        "city_id": location.get("city"),
        "country_code": location.get("country"),
        "latitude": coordinates.get("latitude"),
        "longitude": coordinates.get("longitude"),
        "address": location.get("address"),
        "post_code": location.get("post_code"),
        "location_type": location.get("type"),
    }


# Worker that parses one attraction detail file and writes it in batches, using its own session and the shared write lock
def process_attraction_detail_file(file_path):
    attraction_batch = []
    localized_batch = []
    photo_batch = []

    session = SessionLocal()

    try:
        print(f"Processing {file_path}")

        with open(file_path, "rb") as f:
            for item in ijson.items(f, "item"):

                attraction_batch.append(_build_attraction_row(item))

                for lang, name in item.get("name", {}).items():
                    localized_batch.append(
                        {
                            "attraction_id": item["id"],
                            "language_code": lang,
                            "name": name,
                            "description": item.get(
                                "long_description", {}
                            ).get(lang),
                        }
                    )

                for photo in item.get("photos", []):
                    photo_batch.append(
                        {
                            "attraction_id": item["id"],
                            "photo_url": photo["url"],
                        }
                    )

                if len(attraction_batch) >= BATCH_SIZE:
                    with db_write_lock:
                        flush_attractions(session, attraction_batch)
                        flush_localized(session, localized_batch)
                        flush_photos(session, photo_batch)
                        session.commit()

                    attraction_batch.clear()
                    localized_batch.clear()
                    photo_batch.clear()

        # Flush whatever is left over after the file has been fully read
        with db_write_lock:
            flush_attractions(session, attraction_batch)
            flush_localized(session, localized_batch)
            flush_photos(session, photo_batch)
            session.commit()

    finally:
        session.close()


# Import attraction details, localized text and photos using a thread pool over all files
def import_attraction_details():
    folder = DATA_DIR / "attraction_details"
    files = list(folder.rglob("*.json"))

    if not files:
        print("No attraction detail files found")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(executor.map(process_attraction_detail_file, files))


# Worker that parses one reviews file, skipping reviews with no matching attraction, and returns the skipped count
def process_review_file(file_path, existing_attractions):
    batch = []
    skipped_reviews = 0

    session = SessionLocal()

    try:
        print(f"Processing {file_path}")

        with open(file_path, "rb") as f:
            for item in ijson.items(f, "item"):

                attraction_id = item.get("attraction")

                if attraction_id not in existing_attractions:
                    skipped_reviews += 1
                    print(
                        f"Skipping review {item.get('id')} "
                        f"-> missing attraction {attraction_id}"
                    )
                    continue

                review_date = None
                if item.get("date"):
                    review_date = datetime.fromisoformat(
                        item["date"]
                    ).date()

                batch.append(
                    {
                        "id": item["id"],
                        "attraction_id": attraction_id,
                        "author_name": item.get("author"),
                        "author_country_code": item.get(
                            "author_country_code"
                        ),
                        "rating": item.get("rating"),
                        "review_text": item.get("text"),
                        "language_code": item.get("language"),
                        "review_date": review_date,
                    }
                )

                if len(batch) >= BATCH_SIZE:
                    with db_write_lock:
                        flush_reviews(session, batch)
                        session.commit()

                    print(f"Inserted {len(batch)} reviews")
                    batch.clear()

        # Flush whatever is left over after the file has been fully read
        if batch:
            with db_write_lock:
                flush_reviews(session, batch)
                session.commit()

            print(f"Inserted final {len(batch)} reviews")

    finally:
        session.close()

    return skipped_reviews


# Import reviews using a thread pool over all files, after loading existing attraction ids once up front
def import_reviews(session):
    print("Loading attraction ids...")

    existing_attractions = set(
        session.execute(select(Attraction.id)).scalars().all()
    )

    print(f"Loaded {len(existing_attractions)} attractions")

    folder = DATA_DIR / "reviews"
    files = list(folder.rglob("*.json"))

    if not files:
        print("No review files found")
        return

    total_skipped = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                process_review_file, file_path, existing_attractions
            )
            for file_path in files
        ]

        for future in futures:
            total_skipped += future.result()

    print(f"\nSkipped reviews: {total_skipped}")


# Worker that parses one review scores file and writes it in batches
def process_review_score_file(file_path):
    batch = []

    session = SessionLocal()

    try:
        print(f"Processing {file_path}")

        with open(file_path, "rb") as f:
            for item in ijson.items(f, "item"):

                attraction_id = item["id"]

                for score_type, score_data in item.get(
                    "breakdown", {}
                ).items():
                    batch.append(
                        {
                            "attraction_id": attraction_id,
                            "score_type": score_type,
                            "score": score_data.get("score"),
                            "review_count": score_data.get(
                                "number_of_reviews"
                            ),
                        }
                    )

                if len(batch) >= BATCH_SIZE:
                    with db_write_lock:
                        flush_review_scores(session, batch)
                        session.commit()

                    batch.clear()

        # Flush whatever is left over after the file has been fully read
        if batch:
            with db_write_lock:
                flush_review_scores(session, batch)
                session.commit()

    finally:
        session.close()


# Import review score breakdowns using a thread pool over all files
def import_review_scores():
    folder = DATA_DIR / "reviews_scores"
    files = list(folder.rglob("*.json"))

    if not files:
        print("No review score files found")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(executor.map(process_review_score_file, files))


# Run the full import pipeline in order and print total elapsed time
def run_import():
    start = time.time()

    create_tables()

    session = SessionLocal()

    try:
        import_attraction_details()
        import_reviews(session)
        import_review_scores()

    finally:
        session.close()

    print(f"Completed in {time.time() - start:.2f} seconds")