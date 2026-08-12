from django.core.management.base import BaseCommand

from adcampaigner.pipeline import AdCampaignerGenerationRunner


class Command(BaseCommand):

    help = "Generate AdCampaigner property feeds"

    def handle(self, *args, **options):
        AdCampaignerGenerationRunner().run()