from pyspark.sql import functions as F

EMPTY_SCHEMA = "country_code STRING, code STRING, name STRING"


# Resolves location codes: city > district > landmark > region
class LocationMappingReader:

    FILES = (
        ("city.json", "city_code", "city", 1),
        ("district.json", "district_code", "district", 2),
        ("landmark.json", "landmark_code", "landmark", 3),
        ("region.json", "region_code", "region", 4),
    )

    @classmethod
    def read(cls, spark, data_dir):
        base = data_dir / "static" / "location_mapping"

        if not base.exists():
            return spark.createDataFrame([], EMPTY_SCHEMA)

        frames = cls._read_country_frames(spark, base)

        if not frames:
            return spark.createDataFrame([], EMPTY_SCHEMA)

        return cls._merge_by_priority(frames)

    @classmethod
    def _read_country_frames(cls, spark, base):
        frames = []

        for country_dir in sorted(base.iterdir()):
            if not country_dir.is_dir():
                continue

            country_code = country_dir.name.lower()

            for filename, code_field, name_field, priority in cls.FILES:
                file_path = country_dir / filename

                if not file_path.exists():
                    continue

                df = (
                    spark.read.option("multiLine", True)
                    .json(str(file_path))
                    .select(
                        F.lit(country_code).alias("country_code"),
                        F.col(code_field).cast("string").alias("code"),
                        F.col(name_field).alias("name"),
                        F.lit(priority).alias("priority"),
                    )
                )
                frames.append(df)

        return frames

    @staticmethod
    def _merge_by_priority(frames):
        combined = frames[0]

        for df in frames[1:]:
            combined = combined.unionByName(df)

        window = combined.groupBy("country_code", "code").agg(
            F.min("priority").alias("min_priority")
        )

        return (
            combined.join(window, ["country_code", "code"])
            .filter(F.col("priority") == F.col("min_priority"))
            .select("country_code", "code", "name")
            .dropDuplicates(["country_code", "code"])
        )
