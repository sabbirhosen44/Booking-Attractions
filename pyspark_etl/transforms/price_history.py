from pyspark.sql import functions as F


# Splits search rows into matched/skipped, builds price + update rows
class PriceHistoryTransform:

    @classmethod
    def build(cls, search_df, known_ids_df):
        joined = search_df.join(
            known_ids_df.withColumnRenamed("id", "sid"),
            search_df.id == F.col("sid"),
            "left",
        )

        matched = joined.filter(F.col("country_code").isNotNull())
        skipped = joined.filter(F.col("country_code").isNull())

        check_in, check_out = cls._extract_dates(matched)

        price_history_out = cls._build_price_history(matched, check_in, check_out)
        pricing_updates = cls._build_pricing_updates(matched)
        date_updates = cls._build_date_updates(matched, check_in, check_out)
        skips_out = cls._build_skips(skipped)

        return price_history_out, skips_out, pricing_updates, date_updates

    @staticmethod
    def _extract_dates(matched):
        web_url = F.col("urls.web.detail")
        check_in = F.regexp_extract(web_url, r"start_date=(\d{4}-\d{2}-\d{2})", 1)
        check_out = F.regexp_extract(web_url, r"end_date=(\d{4}-\d{2}-\d{2})", 1)

        return check_in, check_out

    @staticmethod
    def _build_price_history(matched, check_in, check_out):
        return matched.select(
            F.col("id").alias("property_id"),
            F.lit("111").alias("feed"),
            F.to_json(F.col("price")).alias("price"),
            F.when(check_in != "", F.to_date(check_in)).alias("check_in"),
            F.when(check_out != "", F.to_date(check_out)).alias("check_out"),
            F.lower(F.coalesce(F.col("country_code"), F.lit("xx"))).alias("country_code"),
            F.current_timestamp().alias("created_at"),
        )

    @staticmethod
    def _build_pricing_updates(matched):
        return matched.filter(
            F.col("price.currency").isNotNull() & F.col("price.total").isNotNull()
        ).select(
            F.col("id"),
            F.col("price.currency").alias("currency"),
            F.col("price.total").alias("usd_price"),
        ).dropDuplicates(["id"])

    @staticmethod
    def _build_date_updates(matched, check_in, check_out):
        return matched.filter((check_in != "") | (check_out != "")).select(
            F.col("id"),
            F.when(check_in != "", check_in).alias("check_in"),
            F.when(check_out != "", check_out).alias("check_out"),
        ).dropDuplicates(["id"])

    @staticmethod
    def _build_skips(skipped):
        return skipped.select(
            F.col("id").alias("property_id"),
            F.lit("111").alias("feed"),
            F.lit("price snapshot references an attraction not yet imported").alias("reason"),
            F.lit("import_attractions_iceberg").alias("updated_by"),
            F.current_timestamp().alias("updated_at"),
        ).dropDuplicates(["property_id"])
