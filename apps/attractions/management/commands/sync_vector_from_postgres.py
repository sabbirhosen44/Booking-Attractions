from django.core.management.base import BaseCommand

from vector_etl.sync import VectorSyncRunner


class Command(BaseCommand):
    help = "Syncs rental_property from Postgres into Qdrant - adds new rows, removes deleted ones."

    def handle(self, *args, **options):
        VectorSyncRunner().run()