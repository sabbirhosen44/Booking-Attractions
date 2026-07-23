from core.utils.json_reader import JsonReader
from core.utils.location_mapping_reader import LocationMappingReader
from elasticsearch_etl.client import ESClient
from elasticsearch_etl.config import ESConfig
from elasticsearch_etl.indices.index_manager import IndexManager
from elasticsearch_etl.services import ESIndexService
from elasticsearch_etl.transforms.price_history import PriceHistoryTransform
from elasticsearch_etl.transforms.property_reviews import PropertyReviewsTransform
from elasticsearch_etl.transforms.rental_property import RentalPropertyTransform


# Runs all 4 import stages in dependency order
class ElasticsearchDataImportRunner:
    def __init__(self):
        self.client = ESClient.get()
        self.svc = ESIndexService(self.client)
        self.location_lookup = LocationMappingReader(ESConfig.DATA_DIR / "static")
        self.property_transform = RentalPropertyTransform(self.location_lookup)
        self.known_property_ids: set[str] = set()

    def run(self):
        IndexManager.create_indices_if_not_exist(self.client)
        self._import_attraction_details()
        self._import_reviews()
        self._import_price_history()
        print("Elasticsearch import complete.")
        print(f"Known attraction ids: {len(self.known_property_ids)}")

    def _import_attraction_details(self):
        print("Processing attraction_details...")
        folder = ESConfig.DATA_DIR / "attraction_details"
        property_batch, localize_batch, image_batch = [], [], []

        for record in JsonReader.iter_records(folder):
            self.known_property_ids.add(record["id"])

            property_doc = self.property_transform.build_property_doc(record)
            localize_docs = self.property_transform.build_localize_docs(
                record, property_doc["property_slug"]
            )
            image_docs = self.property_transform.build_image_docs(record)

            property_batch.append(property_doc)
            localize_batch.extend(localize_docs)
            image_batch.extend(image_docs)

            if len(property_batch) >= ESConfig.BATCH_SIZE:
                self._flush_attraction_details(property_batch, localize_batch, image_batch)
                property_batch, localize_batch, image_batch = [], [], []

        self._flush_attraction_details(property_batch, localize_batch, image_batch)

    def _flush_attraction_details(self, property_batch, localize_batch, image_batch):
        if property_batch:
            self.svc.bulk_index("rental_property", property_batch, id_field="id")
        if localize_batch:
            self.svc.bulk_index("rental_property_localize", localize_batch)
        if image_batch:
            self.svc.bulk_index("property_image_meta", image_batch)

    def _import_reviews(self):
        print("Processing reviews...")
        folder = ESConfig.DATA_DIR / "reviews"
        matched_batch, skip_batch = [], []

        for record in JsonReader.iter_records(folder):
            attraction_id = record.get("attraction")
            if attraction_id not in self.known_property_ids:
                skip_batch.append(
                    PropertyReviewsTransform.build_skip_doc(
                        record,
                        reason=f"review {record.get('id')} references unknown attraction",
                    )
                )
                continue
            matched_batch.append(PropertyReviewsTransform.build_doc(record))

            if len(matched_batch) >= ESConfig.BATCH_SIZE:
                self.svc.bulk_index("property_reviews", matched_batch, id_field="id")
                matched_batch = []

        if matched_batch:
            self.svc.bulk_index("property_reviews", matched_batch, id_field="id")
        if skip_batch:
            self.svc.bulk_index("skip_properties", skip_batch, id_field="property_id")

    def _import_price_history(self):
        print("Processing search / price_history...")
        folder = ESConfig.DATA_DIR / "search"
        matched_batch, skip_batch = [], []

        for record in JsonReader.iter_records(folder):
            attraction_id = record.get("id")
            if attraction_id not in self.known_property_ids:
                skip_batch.append(
                    PriceHistoryTransform.build_skip_doc(
                        record, reason="search record references unknown attraction"
                    )
                )
                continue
            matched_batch.append(PriceHistoryTransform.build_doc(record))

            if len(matched_batch) >= ESConfig.BATCH_SIZE:
                self.svc.bulk_index("price_history", matched_batch)
                matched_batch = []

        if matched_batch:
            self.svc.bulk_index("price_history", matched_batch)
        if skip_batch:
            self.svc.bulk_index("skip_properties", skip_batch, id_field="property_id")