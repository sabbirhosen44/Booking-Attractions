from qdrant_client import QdrantClient

from vector_etl.config import VectorConfig


# Singleton Qdrant client, local docker instance
class VectorClient:
    _instance = None

    @classmethod
    def get(cls) -> QdrantClient:
        if cls._instance is None:
            cls._instance = QdrantClient(host=VectorConfig.HOST, port=VectorConfig.PORT)
        return cls._instance
