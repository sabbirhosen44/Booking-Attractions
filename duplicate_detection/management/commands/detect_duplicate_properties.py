from django.core.management.base import BaseCommand

from duplicate_detection.pipeline import DuplicateDetectionRunner


class Command(BaseCommand):
    help = "Detects duplicate rental_property rows via vector similarity, groups them with no loops."

    def handle(self, *args, **options):
        DuplicateDetectionRunner().run()
