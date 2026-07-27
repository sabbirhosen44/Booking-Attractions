from apps.attractions.models import RentalProperty
from vector_etl.schema_fields import RENTAL_PROPERTY_FIELDS

class PostgresRentalPropertyReader:
    @staticmethod
    def iter_batches(batch_size:int):
        queryset = RentalProperty.objects.values(*RENTAL_PROPERTY_FIELDS).order_by("id").iterator(chunk_size = batch_size)
        
        batch = []
        for row in queryset:
            batch.append(row)
            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch