from pyspark.sql import functions as F
from pyspark.sql.window import Window

from pyspark_etl.transforms.slug import SlugTransform


# Builds RentalProperty/Localize/ImageMeta frames from attraction_details
class RentalPropertyTransform:

    @staticmethod
    def _truncate(col, length):
        return F.substring(col, 1, length)

    @classmethod
    def _pick_primary_location(cls, details_df):
        exploded = details_df.select(
            "id",
            F.posexplode("locations").alias("pos", "location"),
        )

        priority = F.when(F.col("location.type") == "departure", 1).otherwise(2)
        window = Window.partitionBy("id").orderBy(priority, "pos")

        return (
            exploded.withColumn("rn", F.row_number().over(window))
            .filter(F.col("rn") == 1)
            .select(
                "id",
                F.col("location.address").alias("loc_address"),
                F.col("location.city").alias("loc_city_code"),
                F.col("location.country").alias("loc_country"),
                F.col("location.post_code").alias("loc_post_code"),
                F.col("location.coordinates.latitude").alias("loc_latitude"),
                F.col("location.coordinates.longitude").alias("loc_longitude"),
            )
        )

    @classmethod
    def _build_base(cls, details_df, location_lookup_df):
        primary_location = cls._pick_primary_location(details_df)

        base = details_df.join(primary_location, "id", "left").withColumn(
            "country_code", F.lower(F.coalesce(F.col("loc_country"), F.lit("xx")))
        )

        return base.join(
            location_lookup_df,
            (base.country_code == location_lookup_df.country_code)
            & (base.loc_city_code.cast("string") == location_lookup_df.code),
            "left",
        ).select(base["*"], location_lookup_df["name"].alias("city_name"))

    @classmethod
    def _build_property_df(cls, base):
        property_name = F.coalesce(
            F.col("name").getItem("en-us"),
            F.element_at(F.map_values(F.col("name")), 1),
            F.col("id"),
        )
        photo_urls = F.transform(F.coalesce(F.col("photos"), F.array()), lambda p: p["url"])
        slug = SlugTransform.udf()(property_name)
        point_wkt = F.when(
            F.col("loc_latitude").isNotNull() & F.col("loc_longitude").isNotNull(),
            F.concat(
                F.lit("POINT("), F.col("loc_longitude"), F.lit(" "), F.col("loc_latitude"), F.lit(")")
            ),
        )

        return base.select(
            F.col("id"),
            cls._truncate(F.col("id"), 100).alias("booking_id"),
            F.lit(111).alias("feed"),
            cls._truncate(property_name, 450).alias("property_name"),
            slug.alias("property_slug"),
            F.lit("attraction").alias("property_type"),
            F.coalesce(F.col("categories"), F.array()).alias("activity_categories"),
            F.coalesce(F.col("badges"), F.array()).alias("property_attributes"),
            F.col("ratings.score").alias("review_score_general"),
            F.col("ratings.score").alias("review_score"),
            F.col("ratings.number_of_reviews").cast("int").alias("number_of_review"),
            F.coalesce(F.col("supported_languages"), F.array()).alias("languages"),
            cls._truncate(F.concat_ws(",", F.col("supported_languages")), 250).alias(
                "supported_languages"
            ),
            F.slice(photo_urls, 1, 15).alias("images"),
            F.size(photo_urls).alias("uploaded_image_count"),
            cls._truncate(F.col("urls.web.detail"), 600).alias("feed_provider_url"),
            F.to_json(F.struct(
                F.col("urls.web.detail").alias("web"),
                F.col("urls.app.detail").alias("app"),
            )).alias("partners_url"),
            cls._truncate(F.col("loc_address"), 500).alias("display"),
            cls._truncate(F.col("loc_post_code"), 50).alias("zip_code"),
            F.col("country_code"),
            cls._truncate(F.col("city_name"), 250).alias("city"),
            cls._truncate(F.col("loc_city_code").cast("string"), 500).alias("location_id"),
            point_wkt.alias("latlon"),
            point_wkt.alias("geography_latlon"),
            F.current_timestamp().alias("created_at"),
            F.current_timestamp().alias("updated_at"),
        ).dropDuplicates(["id"])

    @classmethod
    def _build_localize_df(cls, base, property_df):
        slug_by_id = property_df.select(F.col("id").alias("property_id"), "property_slug")

        return (
            base.select(
                "id",
                F.explode(F.map_entries(F.col("name"))).alias("entry"),
                "long_description",
                "loc_address",
                "country_code",
            )
            .select(
                F.col("id").alias("property_id"),
                F.lit(111).alias("feed"),
                cls._truncate(F.col("entry.key"), 50).alias("language"),
                cls._truncate(F.col("entry.value"), 450).alias("property_name"),
                F.element_at(F.col("long_description"), F.col("entry.key")).alias(
                    "property_description"
                ),
                F.lit("attraction").alias("property_type"),
                cls._truncate(F.col("loc_address"), 500).alias("address"),
                F.col("country_code"),
            )
            .join(slug_by_id, "property_id", "left")
            .select(
                "property_id", "feed", "language", "property_name", "property_description",
                "property_slug", "property_type", "address", "country_code",
            )
            .dropDuplicates(["property_id", "language", "country_code"])
        )

    @staticmethod
    def _build_image_df(base):
        photo_urls = F.transform(F.coalesce(F.col("photos"), F.array()), lambda p: p["url"])

        return base.select(
            F.col("id").alias("property_id"),
            F.lit("111").alias("feed"),
            F.explode(photo_urls).alias("url"),
            F.col("country_code"),
        ).dropDuplicates(["property_id", "url"])

    @classmethod
    def build(cls, details_df, location_lookup_df):
        base = cls._build_base(details_df, location_lookup_df)
        property_df = cls._build_property_df(base)
        localize_df = cls._build_localize_df(base, property_df)
        image_df = cls._build_image_df(base)

        return property_df, localize_df, image_df
