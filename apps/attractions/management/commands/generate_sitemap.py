from django.core.management.base import BaseCommand

from sitemap_generator.pipeline import SitemapGenerationRunner


class Command(BaseCommand):
    help = "Generate sitemap"

    def handle(self, *args, **options):
        SitemapGenerationRunner().run()