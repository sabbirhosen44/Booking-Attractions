from pyspark.sql import functions as F


# Splits reviews into matched/skipped, builds review + skip rows
class PropertyReviewsTransform:

    @staticmethod
    def _truncate(col, length):
        return F.substring(col, 1, length)

    @classmethod
    def build(cls, reviews_df, known_ids_df):
        joined = reviews_df.join(
            known_ids_df.withColumnRenamed("id", "attraction"),
            "attraction",
            "left",
        )

        matched = joined.filter(F.col("country_code").isNotNull())
        skipped = joined.filter(F.col("country_code").isNull())

        reviews_out = matched.select(
            F.col("id"),
            F.col("attraction").alias("property_id"),
            F.lit("111").alias("feed"),
            F.lower(F.coalesce(F.col("country_code"), F.lit("xx"))).alias("country_code"),
            cls._truncate(F.coalesce(F.col("language"), F.lit("en")), 3).alias("language_code"),
            F.col("rating").cast("double").alias("score"),
            F.col("text").alias("summary"),
            F.to_json(F.struct(
                F.col("author").alias("name"),
                F.col("author_country_code").alias("country"),
            )).alias("reviewer"),
            F.to_timestamp(F.col("date")).alias("review_date"),
        ).dropDuplicates(["id"])

        skips_out = skipped.select(
            F.col("attraction").alias("property_id"),
            F.lit("111").alias("feed"),
            F.concat(
                F.lit("review "),
                F.coalesce(F.col("id"), F.lit("")),
                F.lit(" references an attraction not yet imported"),
            ).alias("reason"),
            F.lit("import_attractions_iceberg").alias("updated_by"),
            F.current_timestamp().alias("updated_at"),
        ).dropDuplicates(["property_id"])

        return reviews_out, skips_out
