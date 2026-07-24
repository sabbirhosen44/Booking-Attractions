from qdrant_client.models import Distance, VectorParams

from vector_etl.config import VectorConfig


# Creates the collection if missing, does not migrate existing one
class CollectionManager:
    @staticmethod
    def create_if_not_exists(client) -> None:
        existing = [c.name for c in client.get_collections().collections]
        if VectorConfig.COLLECTION_NAME in existing:
            print(f"Already exists: {VectorConfig.COLLECTION_NAME}")
            return

        client.create_collection(
            collection_name=VectorConfig.COLLECTION_NAME,
            vectors_config=VectorParams(size=VectorConfig.VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created collection: {VectorConfig.COLLECTION_NAME}")
