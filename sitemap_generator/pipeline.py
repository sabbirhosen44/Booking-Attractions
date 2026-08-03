from sitemap_generator.config import SitemapConfig
from sitemap_generator.postgres_reader import SitemapPostgresReader
from sitemap_generator.property_sitemap_builder import PropertySitemapBuilder
from sitemap_generator.sitemap_index_builder import SitemapIndexBuilder
from sitemap_generator.writer import SitemapWriter


# Generates property sitemap, nearby property sitemap and sitemap index
class SitemapGenerationRunner:
    BATCH_SIZE = 1000

    def run(self):
        filenames = []

        filenames.append(self._write_property_sitemap())
        filenames.append(self._write_nearby_property_sitemap())

        self._write_index(filenames)

        print(f"Generated {len(filenames)} sitemap files in {SitemapConfig.OUTPUT_DIR}")

    def _write_property_sitemap(self) -> str:
        print("Building property sitemap...")

        rows = []

        for batch in SitemapPostgresReader.iter_property_batches(self.BATCH_SIZE):
            rows.extend(batch)

        xml_content = PropertySitemapBuilder.build_urlset(rows)

        filename = "property-sitemap"

        SitemapWriter.write(filename, xml_content)

        print(f"Wrote {filename} ({len(rows)} urls)")

        return filename

    def _write_nearby_property_sitemap(self) -> str:
        print("Building nearby property sitemap...")

        rows = []

        for batch in SitemapPostgresReader.iter_nearby_property_batches(self.BATCH_SIZE):
            rows.extend(batch)

        xml_content = PropertySitemapBuilder.build_urlset(rows)

        filename = "nearby-property-sitemap"

        SitemapWriter.write(filename, xml_content)

        print(f"Wrote {filename} ({len(rows)} urls)")

        return filename

    @staticmethod
    def _write_index(filenames: list[str]):
        xml_content = SitemapIndexBuilder.build(filenames)

        SitemapWriter.write("site-map-all", xml_content)

        print("Wrote site-map-all")