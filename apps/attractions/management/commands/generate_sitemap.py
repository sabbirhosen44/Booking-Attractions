from django.core.management.base import BaseCommand

from sitemap_generator.pipeline import SitemapGenerationRunner


class Command(BaseCommand):
    help = "Generates sitemap XML files from rental_property, mirrors rentbyowner's structure."

    def handle(self, *args, **options):
        SitemapGenerationRunner().run()
