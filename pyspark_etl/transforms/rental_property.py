from pyspark.sql import functions as F
from pyspark.sql.window import Window

from pyspark_etl.transforms.slug import slugify_udf


def _truncate(col, length):
    return F.substring(col, 1, length)


# Explodes the locations array and picks one row per attraction
def _pick_primary_location(details_df):
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


# Builds the RentalProperty, RentalPropertyLocalize and PropertyImageMeta DataFrames from a raw attraction_details DataFrame
def build_rental_property_frames(details_df, location_lookup_df):
    primary_location = _pick_primary_location(details_df)

    base = details_df.join(primary_location, "id", "left").withColumn(
        "country_code", F.lower(F.coalesce(F.col("loc_country"), F.lit("xx")))
    )

    base = base.join(
        location_lookup_df,
        (base.country_code == location_lookup_df.country_code)
        & (base.loc_city_code.cast("string") == location_lookup_df.code),
        "left",
    ).select(base["*"], location_lookup_df["name"].alias("city_name"))

    property_name = F.coalesce(
        F.col("name").getItem("en-us"),
        F.element_at(F.map_values(F.col("name")), 1),
        F.col("id"),
    )
    photo_urls = F.transform(F.coalesce(F.col("photos"), F.array()), lambda p: p["url"])
    slug = slugify_udf(property_name)
    point_wkt = F.when(
        F.col("loc_latitude").isNotNull() & F.col("loc_longitude").isNotNull(),
        F.concat(F.lit("POINT("), F.col("loc_longitude"), F.lit(" "), F.col("loc_latitude"), F.lit(")")),
    )

    property_df = base.select(
        F.col("id"),
        _truncate(F.col("id"), 100).alias("booking_id"),
        F.lit(111).alias("feed"),
        _truncate(property_name, 450).alias("property_name"),
        slug.alias("property_slug"),
        F.lit("attraction").alias("property_type"),
        F.coalesce(F.col("categories"), F.array()).alias("activity_categories"),
        F.coalesce(F.col("badges"), F.array()).alias("property_attributes"),
        F.col("ratings.score").alias("review_score_general"),
        F.col("ratings.score").alias("review_score"),
        F.col("ratings.number_of_reviews").cast("int").alias("number_of_review"),
        F.coalesce(F.col("supported_languages"), F.array()).alias("languages"),
        _truncate(F.concat_ws(",", F.col("supported_languages")), 250).alias("supported_languages"),
        F.slice(photo_urls, 1, 15).alias("images"),
        F.size(photo_urls).alias("uploaded_image_count"),
        _truncate(F.col("urls.web.detail"), 600).alias("feed_provider_url"),
        F.to_json(F.struct(
            F.col("urls.web.detail").alias("web"),
            F.col("urls.app.detail").alias("app"),
        )).alias("partners_url"),
        _truncate(F.col("loc_address"), 500).alias("display"),
        _truncate(F.col("loc_post_code"), 50).alias("zip_code"),
        F.col("country_code"),
        _truncate(F.col("city_name"), 250).alias("city"),
        _truncate(F.col("loc_city_code").cast("string"), 500).alias("location_id"),
        point_wkt.alias("latlon"),
        point_wkt.alias("geography_latlon"),
        F.current_timestamp().alias("created_at"),
        F.current_timestamp().alias("updated_at"),
    ).dropDuplicates(["id"])

    slug_by_id = property_df.select(F.col("id").alias("property_id"), "property_slug")

    localize_df = (
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
            _truncate(F.col("entry.key"), 50).alias("language"),
            _truncate(F.col("entry.value"), 450).alias("property_name"),
            F.element_at(F.col("long_description"), F.col("entry.key")).alias("property_description"),
            F.lit("attraction").alias("property_type"),
            _truncate(F.col("loc_address"), 500).alias("address"),
            F.col("country_code"),
        )
        .join(slug_by_id, "property_id", "left")
        .select(
            "property_id", "feed", "language", "property_name", "property_description",
            "property_slug", "property_type", "address", "country_code",
        )
        .dropDuplicates(["property_id", "language", "country_code"])
    )

    image_df = base.select(
        F.col("id").alias("property_id"),
        F.lit("111").alias("feed"),
        F.explode(photo_urls).alias("url"),
        F.col("country_code"),
    ).dropDuplicates(["property_id", "url"])

    return property_df, localize_df, image_df