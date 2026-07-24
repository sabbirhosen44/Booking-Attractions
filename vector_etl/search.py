from vector_etl.client import VectorClient
from vector_etl.config import VectorConfig
from vector_etl.embedder import Embedder
from vector_etl.point_id import PointId


# Finds rental_property records similar to a text query or an existing property
class SimilaritySearch:
    @staticmethod
    def search_by_text(query: str, top_k: int = 5) -> list:
        client = VectorClient.get()
        vector = Embedder.encode_one(query)

        results = client.query_points(
            collection_name=VectorConfig.COLLECTION_NAME,
            query=vector,
            limit=top_k,
        )
        return [{"score": r.score, **r.payload} for r in results.points]

    @staticmethod
    def search_similar_to_property(property_id: str, top_k: int = 5) -> list:
        client = VectorClient.get()
        point_id = PointId.for_property(property_id)

        existing = client.retrieve(
            collection_name=VectorConfig.COLLECTION_NAME,
            ids=[point_id],
            with_vectors=True,
        )
        if not existing:
            return []

        results = client.query_points(
            collection_name=VectorConfig.COLLECTION_NAME,
            query=existing[0].vector,
            limit=top_k + 1,  # +1 because the property matches itself first
        )
        return [
            {"score": r.score, **r.payload}
            for r in results.points
            if r.payload.get("id") != property_id
        ][:top_k]