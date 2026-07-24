from django.core.management.base import BaseCommand

from vector_etl.search import SimilaritySearch


class Command(BaseCommand):
    help = "Finds rental_property records similar to a text query or a property id."

    def add_arguments(self, parser):
        parser.add_argument("--query", type=str, help="Free-text search query")
        parser.add_argument("--property-id", type=str, help="Find properties similar to this one")
        parser.add_argument("--top-k", type=int, default=5)

    def handle(self, *args, **options):
        top_k = options["top_k"]

        if options["property_id"]:
            results = SimilaritySearch.search_similar_to_property(options["property_id"], top_k)
        elif options["query"]:
            results = SimilaritySearch.search_by_text(options["query"], top_k)
        else:
            self.stdout.write("Provide --query \"text\" or --property-id PRxxxx")
            return

        for r in results:
            self.stdout.write(f"{r['score']:.4f}  {r['property_id']}  {r['property_name']}  ({r['city']}, {r['country_code']})")
