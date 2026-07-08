from django.core.management.base import BaseCommand

from attractions.services import run_import


class Command(BaseCommand):
    help = "Import Booking Attraction JSON data"

    def handle(self, *args, **options):
        run_import()