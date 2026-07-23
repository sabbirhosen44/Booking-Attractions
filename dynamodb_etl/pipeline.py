from core.utils.json_reader import JsonReader
from core.utils.location_mapping_reader import LocationMappingReader
from dynamodb_etl.client import DynamoClient
from dynamodb_etl.config import DynamoConfig
from dynamodb_etl.tables.table_manager import TableManager
from dynamodb_etl.services import DynamoWriteService
from dynamodb_etl.transforms.price_history import PriceHistoryTransform
from dynamodb_etl.transforms.property_reviews import PropertyReviewsTransform
from dynamodb_etl.transforms.rental_property import RentalPropertyTransform


# Runs all 4 import stages in dependency order
class DynamoDataImportRunner:
    def __init__(self):
        self.client = DynamoClient.get()
        self.svc = DynamoWriteService(self.client)
        self.location_lookup = LocationMappingReader(DynamoConfig.DATA_DIR / "static")
        self.property_transform = RentalPropertyTransform(self.location_lookup)
        self.known_property_ids: set[str] = set()

    def run(self):
        TableManager.create_tables_if_not_exist(self.client)
        self._import_attraction_details()
        self._import_reviews()
        self._import_price_history()
        print("DynamoDB import complete.")
        print(f"Known attraction ids: {len(self.known_property_ids)}")

    def _import_attraction_details(self):
        print("Processing attraction_details...")
        folder = DynamoConfig.DATA_DIR / "attraction_details"
        property_batch, localize_batch, image_batch = [], [], []

        for record in JsonReader.iter_records(folder):
            self.known_property_ids.add(record["id"])

            property_item = self.property_transform.build_property_item(record)
            localize_items = self.property_transform.build_localize_items(
                record, property_item["property_slug"]
            )
            image_items = self.property_transform.build_image_items(record)

            property_batch.append(property_item)
            localize_batch.extend(localize_items)
            image_batch.extend(image_items)

            if len(property_batch) >= DynamoConfig.BATCH_SIZE:
                self._flush_attraction_details(property_batch, localize_batch, image_batch)
                property_batch, localize_batch, image_batch = [], [], []

        self._flush_attraction_details(property_batch, localize_batch, image_batch)

    def _flush_attraction_details(self, property_batch, localize_batch, image_batch):
        if property_batch:
            self.svc.batch_write("rental_property", property_batch)
        if localize_batch:
            self.svc.batch_write("rental_property_localize", localize_batch)
        if image_batch:
            self.svc.batch_write("property_image_meta", image_batch)

    def _import_reviews(self):
        print("Processing reviews...")
        folder = DynamoConfig.DATA_DIR / "reviews"
        matched_batch, skip_by_property = [], {}

        for record in JsonReader.iter_records(folder):
            attraction_id = record.get("attraction")
            if attraction_id not in self.known_property_ids:
                skip_item = PropertyReviewsTransform.build_skip_item(
                    record,
                    reason=f"review {record.get('id')} references unknown attraction",
                )
                skip_by_property[skip_item["property_id"]] = skip_item
                continue
            matched_batch.append(PropertyReviewsTransform.build_item(record))

            if len(matched_batch) >= DynamoConfig.BATCH_SIZE:
                self.svc.batch_write("property_reviews", matched_batch)
                matched_batch = []

        if matched_batch:
            self.svc.batch_write("property_reviews", matched_batch)
        if skip_by_property:
            self.svc.batch_write("skip_properties", list(skip_by_property.values()), key_fields=["property_id"])

    def _import_price_history(self):
        print("Processing search / price_history...")
        folder = DynamoConfig.DATA_DIR / "search"
        matched_batch, skip_by_property = [], {}

        for record in JsonReader.iter_records(folder):
            attraction_id = record.get("id")
            if attraction_id not in self.known_property_ids:
                skip_item = PriceHistoryTransform.build_skip_item(
                    record, reason="search record references unknown attraction"
                )
                skip_by_property[skip_item["property_id"]] = skip_item
                continue
            matched_batch.append(PriceHistoryTransform.build_item(record))

            if len(matched_batch) >= DynamoConfig.BATCH_SIZE:
                self.svc.batch_write("price_history", matched_batch)
                matched_batch = []

        if matched_batch:
            self.svc.batch_write("price_history", matched_batch)
        if skip_by_property:
            self.svc.batch_write("skip_properties", list(skip_by_property.values()), key_fields=["property_id"])