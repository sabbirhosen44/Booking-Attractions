from django.core.management.base import BaseCommand

from dynamodb_etl.pipeline import DynamoDataImportRunner


class Command(BaseCommand):
    help = "Imports Booking Attractions data from data/ into DynamoDB."

    def handle(self, *args, **options):
        DynamoDataImportRunner().run()
    
