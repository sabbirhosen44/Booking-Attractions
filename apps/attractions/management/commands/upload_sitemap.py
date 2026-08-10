from django.core.management.base import BaseCommand

from sitemap_generator.storage.sitemap_uploader import SitemapUploader


class Command(BaseCommand):
    help = "Upload sitemap files"

    def handle(self, *args, **options):
        SitemapUploader().run()