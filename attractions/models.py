from sqlalchemy import (
    JSON,
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(String, primary_key=True)
    duration = Column(String)
    rating_score = Column(Numeric(3, 2))
    rating_review_count = Column(Integer)
    categories = Column(JSON, nullable=False, default=list)
    badges = Column(JSON, nullable=False, default=list)
    booking_web_url = Column(Text)
    booking_app_url = Column(Text)
    city_id = Column(Integer)
    country_code = Column(String(10))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    address = Column(Text)
    post_code = Column(String(20))
    location_type = Column(String)

    localized = relationship(
        "AttractionLocalized", back_populates="attraction", cascade="all, delete-orphan"
    )
    photos = relationship(
        "AttractionPhoto", back_populates="attraction", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "AttractionReview", back_populates="attraction", cascade="all, delete-orphan"
    )
    review_scores = relationship(
        "AttractionReviewScore", back_populates="attraction", cascade="all, delete-orphan"
    )


class AttractionLocalized(Base):
    __tablename__ = "attraction_localized"
    __table_args__ = (
        UniqueConstraint(
            "attraction_id", "language_code", name="uq_localized_attraction_language"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    attraction_id = Column(
        String, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False
    )
    language_code = Column(String, nullable=False)
    name = Column(String)
    description = Column(Text)

    attraction = relationship("Attraction", back_populates="localized")


class AttractionPhoto(Base):
    __tablename__ = "attraction_photos"
    __table_args__ = (
        UniqueConstraint(
            "attraction_id", "photo_url", name="uq_photos_attraction_url"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    attraction_id = Column(
        String, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False
    )
    photo_url = Column(Text, nullable=False)

    attraction = relationship("Attraction", back_populates="photos")


class AttractionReview(Base):
    __tablename__ = "attraction_reviews"

    id = Column(String, primary_key=True)
    attraction_id = Column(
        String, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False
    )
    author_name = Column(String)
    author_country_code = Column(String(10))
    rating = Column(Integer)
    review_text = Column(Text)
    language_code = Column(String)
    review_date = Column(Date)

    attraction = relationship("Attraction", back_populates="reviews")


class AttractionReviewScore(Base):
    __tablename__ = "attraction_review_scores"
    __table_args__ = (
        UniqueConstraint(
            "attraction_id", "score_type", name="uq_scores_attraction_type"
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    attraction_id = Column(
        String, ForeignKey("attractions.id", ondelete="CASCADE"), nullable=False
    )
    score_type = Column(String, nullable=False)
    score = Column(Numeric(3, 2))
    review_count = Column(Integer)

    attraction = relationship("Attraction", back_populates="review_scores")