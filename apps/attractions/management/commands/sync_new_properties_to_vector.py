from django.core.management.base import BaseCommand

from vector_etl.sync import VectorSyncRunner


class Command(BaseCommand):
    help = "Embeds and syncs only new RentalProperty rows from Postgres into Qdrant."

    def handle(self, *args, **options):
        VectorSyncRunner().run()