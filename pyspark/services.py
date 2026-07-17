from pyspark.catalog.tables import ensure_tables

# Handles saving attraction details, translations, photos and price/date updates in Iceberg
class IcebergAttractionDBService:
    @staticmethod 
    def ensure_tables(spark):
        ensure_tables(spark)
    
    @staticmethod
    def save_properties(spark, df):
        upsert(spark, df, SparkConfig.table("rental_property"), ["id"])
  
    