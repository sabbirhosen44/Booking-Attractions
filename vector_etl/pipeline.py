from qdrant_client.models import PointStruct

from core.utils.json_reader import JsonReader
from core.utils.location_mapping_reader import LocationMappingReader
from vector_etl.client import VectorClient
from vector_etl.collection_manager import CollectionManager
from vector_etl.config import VectorConfig
from vector_etl.embedder import Embedder
from vector_etl.point_id import PointId
from vector_etl.text_builder import TextBuilder
from vector_etl.transforms.rental_property import RentalPropertyPayloadBuilder


# Embeds and upserts rental_property records into Qdrant
class VectorImportRunner:
    def __init__(self):
        self.client = VectorClient.get()
        self.location_lookup = LocationMappingReader(VectorConfig.DATA_DIR / "static")
        self.payload_builder = RentalPropertyPayloadBuilder(self.location_lookup)

    def run(self):
        CollectionManager.create_if_not_exists(self.client)
        print("Processing attraction_details...")

        folder = VectorConfig.DATA_DIR / "attraction_details"
        payloads, texts = [], []
        count = 0

        for record in JsonReader.iter_records(folder):
            payload = self.payload_builder.build(record)
            text = TextBuilder.build(record, payload["city"], payload["country_code"])

            payloads.append(payload)
            texts.append(text)

            if len(payloads) >= VectorConfig.BATCH_SIZE:
                self._flush(payloads, texts)
                count += len(payloads)
                payloads, texts = [], []

        if payloads:
            self._flush(payloads, texts)
            count += len(payloads)

        print(f"Vector import complete. Total embedded: {count}")

    def _flush(self, payloads: list, texts: list):
        vectors = Embedder.encode_batch(texts)
        points = [
            PointStruct(id=PointId.for_property(p["id"]), vector=v, payload=p)
            for p, v in zip(payloads, vectors)
        ]
        self.client.upsert(collection_name=VectorConfig.COLLECTION_NAME, points=points)
