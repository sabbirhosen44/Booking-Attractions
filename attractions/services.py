import time
from datetime import datetime
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

import ijson

from django.conf import settings

from sqlalchemy.dialects.sqlite import insert

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

def create_tables():
    Base.metadata.create_all(bind=engine)
    

def flush_attractions(session, batch):
    if not batch:
        return

    stmt = insert(Attraction)

    stmt = stmt.values(batch)

    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
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
    
def import_attraction_details(session):

    attraction_batch = []
    localized_batch = []
    photo_batch = []

    folder = DATA_DIR / "attraction_details"

    for file in folder.rglob("*.json"):

        print(f"Processing {file}")

        with open(file, "rb") as f:

            for item in ijson.items(f, "item"):

                location = {}

                if item.get("locations"):
                    location = item["locations"][0]

                coordinates = location.get(
                    "coordinates",
                    {},
                )

                attraction_batch.append(
                    {
                        "id": item["id"],
                        "rating_score": item.get(
                            "ratings",
                            {},
                        ).get("score"),
                        "rating_review_count": item.get(
                            "ratings",
                            {},
                        ).get("number_of_reviews"),
                        "categories": item.get(
                            "categories",
                            [],
                        ),
                        "badges": item.get(
                            "badges",
                            [],
                        ),
                        "booking_web_url": item.get(
                            "urls",
                            {},
                        ).get(
                            "web",
                            {},
                        ).get(
                            "detail"
                        ),
                        "booking_app_url": item.get(
                            "urls",
                            {},
                        ).get(
                            "app",
                            {},
                        ).get(
                            "detail"
                        ),
                        "city_id": location.get("city"),
                        "country_code": location.get(
                            "country"
                        ),
                        "latitude": coordinates.get(
                            "latitude"
                        ),
                        "longitude": coordinates.get(
                            "longitude"
                        ),
                        "address": location.get(
                            "address"
                        ),
                        "post_code": location.get(
                            "post_code"
                        ),
                        "location_type": location.get(
                            "type"
                        ),
                    }
                )

                for lang, name in item.get(
                    "name",
                    {},
                ).items():

                    localized_batch.append(
                        {
                            "attraction_id": item["id"],
                            "language_code": lang,
                            "name": name,
                            "description": item.get(
                                "long_description",
                                {},
                            ).get(lang),
                        }
                    )

                for photo in item.get(
                    "photos",
                    [],
                ):

                    photo_batch.append(
                        {
                            "attraction_id": item["id"],
                            "photo_url": photo["url"],
                        }
                    )

                if len(attraction_batch) >= BATCH_SIZE:

                    flush_attractions(
                        session,
                        attraction_batch,
                    )

                    flush_localized(
                        session,
                        localized_batch,
                    )

                    flush_photos(
                        session,
                        photo_batch,
                    )

                    session.commit()

                    attraction_batch.clear()
                    localized_batch.clear()
                    photo_batch.clear()

    flush_attractions(session, attraction_batch)
    flush_localized(session, localized_batch)
    flush_photos(session, photo_batch)

    session.commit()




def import_reviews(session):

    batch = []

    skipped_reviews = 0

    print("Loading attraction ids...")

    existing_attractions = set(
        session.execute(
            select(Attraction.id)
        ).scalars().all()
    )

    print(
        f"Loaded {len(existing_attractions)} attractions"
    )

    folder = DATA_DIR / "reviews"

    for file in folder.rglob("*.json"):

        print(f"Processing {file}")

        with open(file, "rb") as f:

            for item in ijson.items(f, "item"):

                attraction_id = item.get(
                    "attraction"
                )

                if (
                    attraction_id
                    not in existing_attractions
                ):
                    skipped_reviews += 1

                    print(
                        f"Skipping review "
                        f"{item.get('id')} "
                        f"-> missing attraction "
                        f"{attraction_id}"
                    )

                    continue

                review_date = None

                if item.get("date"):
                    review_date = (
                        datetime.fromisoformat(
                            item["date"]
                        ).date()
                    )

                batch.append(
                    {
                        "id": item["id"],
                        "attraction_id": attraction_id,
                        "author_name": item.get(
                            "author"
                        ),
                        "author_country_code": item.get(
                            "author_country_code"
                        ),
                        "rating": item.get(
                            "rating"
                        ),
                        "review_text": item.get(
                            "text"
                        ),
                        "language_code": item.get(
                            "language"
                        ),
                        "review_date": review_date,
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    stmt = insert(
                        AttractionReview
                    )

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

                    session.commit()

                    print(
                        f"Inserted {len(batch)} reviews"
                    )

                    batch.clear()

    if batch:

        stmt = insert(
            AttractionReview
        )

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

        session.commit()

        print(
            f"Inserted final {len(batch)} reviews"
        )

    print(
        f"\nSkipped reviews: "
        f"{skipped_reviews}"
    )


    if batch:

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

        session.commit()
        

def import_review_scores(session):

    batch = []

    folder = DATA_DIR / "reviews_scores"

    for file in folder.rglob("*.json"):

        print(f"Processing {file}")

        with open(file, "rb") as f:

            for item in ijson.items(f, "item"):

                attraction_id = item["id"]

                for score_type, score_data in (
                    item.get(
                        "breakdown",
                        {},
                    ).items()
                ):

                    batch.append(
                        {
                            "attraction_id": attraction_id,
                            "score_type": score_type,
                            "score": score_data.get(
                                "score"
                            ),
                            "review_count": score_data.get(
                                "number_of_reviews"
                            ),
                        }
                    )

                if len(batch) >= BATCH_SIZE:

                    stmt = insert(
                        AttractionReviewScore
                    )

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

                    session.commit()

                    batch.clear()

    if batch:

        stmt = insert(
            AttractionReviewScore
        )

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

        session.commit()
        
def run_import():

    start = time.time()

    create_tables()

    session = SessionLocal()

    try:

        import_attraction_details(session)
        import_reviews(session)
        import_review_scores(session)

    finally:
        session.close()

    print(
        f"Completed in {time.time() - start:.2f} seconds"
    )


