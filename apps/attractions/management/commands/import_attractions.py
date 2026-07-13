from django.core.management.base import BaseCommand

from apps.attractions.services import DataImportRunner


class Command(BaseCommand):
    help = "Import Booking Attraction JSON data"

    def handle(self, *args, **options):
        DataImportRunner().run()