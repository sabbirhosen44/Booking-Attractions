from django.core.management.base import BaseCommand

from elasticsearch_etl.pipeline import ElasticsearchDataImportRunner


class Command(BaseCommand):
    help = "Imports Booking Attractions data from data/ into Elasticsearch."

    def handle(self, *args, **options):
        ElasticsearchDataImportRunner().run()
