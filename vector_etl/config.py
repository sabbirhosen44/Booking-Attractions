from pathlib import Path

from core.configuration import BASE_DIR, VECTOR_DB, IMPORT

PACKAGE_DIR = Path(__file__).resolve().parent


# Qdrant connection and embedding settings
class VectorConfig:
    DATA_DIR = Path(BASE_DIR) / IMPORT["data_dir"]
    HOST = VECTOR_DB["host"]
    PORT = VECTOR_DB.get("port", 6333)
    COLLECTION_NAME = VECTOR_DB.get("collection_name", "rental_property")
    EMBEDDING_MODEL = VECTOR_DB.get("embedding_model", "all-MiniLM-L6-v2")
    VECTOR_SIZE = 384
    BATCH_SIZE = VECTOR_DB.get("batch_size", 100)
