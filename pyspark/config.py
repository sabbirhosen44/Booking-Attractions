from pathlib import Path

from core.configuration import BASE_DIR, ICEBERG, IMPORT


# Centralizes Spark/Iceberg configuration, mirroring ImportConfig's style
class SparkConfig:
    DATA_DIR = Path(BASE_DIR) / IMPORT["data_dir"]
    WAREHOUSE_DIR = Path(BASE_DIR) / ICEBERG["warehouse_dir"]
    CATALOG_NAME = ICEBERG["catalog_name"]
    DATABASE = ICEBERG["database"]
    APP_NAME = "booking_attraction_iceberg_import"
    
    @classmethod
    def table(cls, name):
        return f"{cls.CATALOG_NAME}.{cls.DATABASE}.{name}"