import time
from pyspark.config import SparkConfig
from pyspark.session import get_spark_session
from pyspark.readers.json_reader import read_json_folder
from pyspark.schemas.source import (
    ATTRACTION_DETAILS_SCHEMA,
)
from pyspark.services import IcebergAttractionDBService

# Runs the attraction_details -> reviews -> reviews_scores -> search pipeline
# against Iceberg, mirroring DataImportRunner's stage order in services.py
class IcebergDataImportRunner:
    
    def run(self):
        start = time.time()
        spark = get_spark_session()
        
        try:
            IcebergAttractionDBService.ensure_tables(spark)
            
            print("Processing attraction_details...")
            details_df = read_json_folder(spark,SparkConfig.DATA_DIR / "attraction_details",ATTRACTION_DETAILS_SCHEMA)
        
        finally:
            spark.stop()

        print(f"Completed in {time.time() - start:.2f} seconds")