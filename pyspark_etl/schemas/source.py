from pyspark.sql.types import (
    ArrayType,
    DoubleType,
    LongType,
    MapType,
    StringType,
    StructField,
    StructType,
)


# Explicit schemas for locale-keyed / map-typed raw JSON fields
class SourceSchemas:

    ATTRACTION_DETAILS_SCHEMA = StructType([
        StructField("id", StringType()),
        StructField("name", MapType(StringType(), StringType())),
        StructField("long_description", MapType(StringType(), StringType())),
        StructField("locations", ArrayType(StructType([
            StructField("address", StringType()),
            StructField("city", LongType()),
            StructField("coordinates", StructType([
                StructField("latitude", DoubleType()),
                StructField("longitude", DoubleType()),
            ])),
            StructField("country", StringType()),
            StructField("post_code", StringType()),
            StructField("type", StringType()),
        ]))),
        StructField("urls", StructType([
            StructField("app", StructType([StructField("detail", StringType())])),
            StructField("web", StructType([StructField("detail", StringType())])),
        ])),
        StructField("supported_languages", ArrayType(StringType())),
        StructField("photos", ArrayType(StructType([StructField("url", StringType())]))),
        StructField("categories", ArrayType(StringType())),
        StructField("ratings", StructType([
            StructField("score", DoubleType()),
            StructField("number_of_reviews", LongType()),
        ])),
        StructField("badges", ArrayType(StringType())),
    ])

    REVIEWS_SCHEMA = StructType([
        StructField("attraction", StringType()),
        StructField("id", StringType()),
        StructField("author", StringType()),
        StructField("author_country_code", StringType()),
        StructField("rating", LongType()),
        StructField("text", StringType()),
        StructField("language", StringType()),
        StructField("date", StringType()),
    ])

    REVIEWS_SCORES_SCHEMA = StructType([
        StructField("id", StringType()),
        StructField("breakdown", MapType(StringType(), StructType([
            StructField("number_of_reviews", LongType()),
            StructField("score", DoubleType()),
        ]))),
    ])

    SEARCH_SCHEMA = StructType([
        StructField("id", StringType()),
        StructField("price", StructType([
            StructField("currency", StringType()),
            StructField("total", DoubleType()),
        ])),
        StructField("urls", StructType([
            StructField("app", StructType([StructField("detail", StringType())])),
            StructField("web", StructType([StructField("detail", StringType())])),
        ])),
        StructField("free_cancellation", StringType()),
    ])

