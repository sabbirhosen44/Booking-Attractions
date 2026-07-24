from django.core.management.base import BaseCommand

from vector_etl.pipeline import VectorImportRunner


class Command(BaseCommand):
    help = "Embeds and imports rental_property data from data/ into Qdrant."

    def handle(self, *args, **options):
        VectorImportRunner().run()
