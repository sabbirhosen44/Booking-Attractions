from django.core.management.base import BaseCommand

from pyspark_etl.pipeline import IcebergDataImportRunner


class Command(BaseCommand):
    help = "Import Booking Attraction JSON data into Iceberg via PySpark"

    def handle(self, *args, **options):
        IcebergDataImportRunner().run()