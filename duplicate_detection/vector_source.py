from qdrant_client.models import QueryRequest

from vector_etl.client import VectorClient
from vector_etl.config import VectorConfig
from duplicate_detection.config import DuplicateDetectionConfig


# Loads all property vectors and finds each one's nearest neighbors
class VectorSource:
    def __init__(self):
        self.client = VectorClient.get()

    def load_all_vectors(self) -> dict:
        vectors = {}
        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=VectorConfig.COLLECTION_NAME,
                limit=500,
                offset=offset,
                with_payload=["id"],
                with_vectors=True,
            )
            for point in points:
                property_id = point.payload.get("id")
                if property_id:
                    vectors[property_id] = point.vector

            if offset is None:
                break

        return vectors

    def find_neighbors(self, vectors: dict) -> dict:
        property_ids = list(vectors.keys())
        neighbors = {}

        for start in range(0, len(property_ids), DuplicateDetectionConfig.QUERY_BATCH_SIZE):
            chunk = property_ids[start:start + DuplicateDetectionConfig.QUERY_BATCH_SIZE]
            requests = [
                QueryRequest(
                    query=vectors[pid],
                    limit=DuplicateDetectionConfig.MAX_MATCHES_PER_PROPERTY,
                    score_threshold=DuplicateDetectionConfig.THRESHOLD,
                    with_payload=True,
                )
                for pid in chunk
            ]
            responses = self.client.query_batch_points(
                collection_name=VectorConfig.COLLECTION_NAME,
                requests=requests,
            )

            for pid, response in zip(chunk, responses):
                neighbors[pid] = [
                    (point.payload.get("id"), point.score)
                    for point in response.points
                    if point.payload.get("id") != pid
                ]

        return neighbors