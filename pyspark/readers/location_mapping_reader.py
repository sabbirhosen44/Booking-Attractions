from pyspark.sql import functions as F

FILES = (
    ("city.json", "city_code", "city", 1),
    ("district.json", "district_code", "district", 2),
    ("landmark.json", "landmark_code", "landmark", 3),
    ("region.json", "region_code", "region", 4),
)


def read_location_mapping(spark, data_dir):
    pass