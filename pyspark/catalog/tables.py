from pyspark.config import SparkConfig

TABLE_DDL = {
    "rental_property": """
        CREATE TABLE IF NOT EXISTS {table} (
            id STRING,
            booking_id STRING,
            feed INT,
            property_name STRING,
            property_slug STRING,
            property_type STRING,
            activity_categories ARRAY<STRING>,
            property_attributes ARRAY<STRING>,
            review_score_general DOUBLE,
            review_score DOUBLE,
            number_of_review INT,
            review_scores STRING,
            languages ARRAY<STRING>,
            supported_languages STRING,
            images ARRAY<STRING>,
            uploaded_image_count INT,
            feed_provider_url STRING,
            partners_url STRING,
            display STRING,
            zip_code STRING,
            country_code STRING,
            city STRING,
            location_id STRING,
            latitude DOUBLE,
            longitude DOUBLE,
            currency STRING,
            usd_price DOUBLE,
            check_in STRING,
            check_out STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING iceberg
        PARTITIONED BY (country_code)
    """,
    "rental_property_localize": """
        CREATE TABLE IF NOT EXISTS {table} (
            property_id STRING,
            feed INT,
            language STRING,
            property_name STRING,
            property_description STRING,
            property_slug STRING,
            property_type STRING,
            address STRING,
            country_code STRING
        ) USING iceberg
        PARTITIONED BY (country_code)
    """,
    "property_image_meta": """
        CREATE TABLE IF NOT EXISTS {table} (
            property_id STRING,
            feed STRING,
            url STRING,
            country_code STRING
        ) USING iceberg
        PARTITIONED BY (country_code)
    """,
    "property_reviews": """
        CREATE TABLE IF NOT EXISTS {table} (
            id STRING,
            property_id STRING,
            feed STRING,
            country_code STRING,
            language_code STRING,
            score DOUBLE,
            summary STRING,
            reviewer STRING,
            review_date TIMESTAMP
        ) USING iceberg
        PARTITIONED BY (country_code)
    """,
    "price_history": """
        CREATE TABLE IF NOT EXISTS {table} (
            property_id STRING,
            feed STRING,
            price STRING,
            check_in DATE,
            check_out DATE,
            country_code STRING,
            created_at TIMESTAMP
        ) USING iceberg
        PARTITIONED BY (country_code)
    """,
    "skip_properties": """
        CREATE TABLE IF NOT EXISTS {table} (
            property_id STRING,
            feed STRING,
            reason STRING,
            updated_by STRING,
            updated_at TIMESTAMP
        ) USING iceberg
    """,
}

# Creates the Iceberg database and all target tables if they don't exist yet
def ensure_tables(spark):
    catalog = SparkConfig.CATALOG_NAME
    db = SparkConfig.DATABASE

    spark.sql(f"CREATE DATABASE IF NOT EXISTS {catalog}.{db}")

    for name, ddl in TABLE_DDL.items():
        spark.sql(ddl.format(table=SparkConfig.table(name)))
