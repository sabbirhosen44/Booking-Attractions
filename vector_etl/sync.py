from qdrant_client.models import PointStruct, PointIdsList

from vector_etl.client import VectorClient
from vector_etl.config import VectorConfig
from vector_etl.embedder import Embedder
from vector_etl.payload_sanitizer import PayloadSanitizer
from vector_etl.point_id import PointId
from vector_etl.postgres_reader import PostgresRentalPropertyReader
from vector_etl.text_builder import TextBuilder


# Embeds only RentalProperty rows not already present in Qdrant
class VectorSyncRunner:
    def __init__(self):
        self.client = VectorClient.get()

    def run(self):
        total_checked = 0
        total_new = 0

        for batch in PostgresRentalPropertyReader.iter_batches(VectorConfig.BATCH_SIZE):
            new_rows = self._filter_new(batch)
            total_checked += len(batch)
            total_new += len(new_rows)

            if new_rows:
                self._embed_and_upsert(new_rows)

        self._delete_removed_properties()

        print(
            f"Checked {total_checked} rows, "
            f"embedded {total_new} new properties."
        )

    def _filter_new(self, rows: list) -> list:
        point_ids = [PointId.for_property(row["id"]) for row in rows]

        existing = self.client.retrieve(
            collection_name=VectorConfig.COLLECTION_NAME,
            ids=point_ids,
            with_payload=False,
            with_vectors=False,
        )
        existing_ids = {p.id for p in existing}

        return [
            row for row, point_id in zip(rows, point_ids)
            if point_id not in existing_ids
        ]

    def _embed_and_upsert(self, rows: list):
        texts = [TextBuilder.build_from_row(row) for row in rows]
        vectors = Embedder.encode_batch(texts)

        points = [
            PointStruct(
                id=PointId.for_property(row["id"]),
                vector=vector,
                payload=PayloadSanitizer.sanitize_row(row),
            )
            for row, vector in zip(rows, vectors)
        ]
        self.client.upsert(collection_name=VectorConfig.COLLECTION_NAME, points=points)
        
    def _delete_removed_properties(self):
        postgres_ids = set()

        for batch in PostgresRentalPropertyReader.iter_batches(VectorConfig.BATCH_SIZE):
            for row in batch:
                postgres_ids.add(PointId.for_property(row["id"]))

        qdrant_ids = set()

        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=VectorConfig.COLLECTION_NAME,
                limit=VectorConfig.BATCH_SIZE,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )

            for point in points:
                qdrant_ids.add(str(point.id))

            if offset is None:
                break

        stale_ids = list(qdrant_ids - postgres_ids)

        if stale_ids:
            self.client.delete(
                collection_name=VectorConfig.COLLECTION_NAME,
                points_selector=PointIdsList(points=stale_ids),
            )

            print(f"Deleted {len(stale_ids)} removed properties.")