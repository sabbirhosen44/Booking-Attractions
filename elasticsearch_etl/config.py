from pathlib import Path

from core.configuration import BASE_DIR, ELASTICSEARCH, IMPORT

PACKAGE_DIR = Path(__file__).resolve().parent


# ES connection and index settings
class ESConfig:
    DATA_DIR = Path(BASE_DIR) / IMPORT["data_dir"]
    HOST = ELASTICSEARCH["host"]
    BATCH_SIZE = ELASTICSEARCH.get("batch_size", 500)

    @classmethod
    def index(cls, name: str) -> str:
        return name