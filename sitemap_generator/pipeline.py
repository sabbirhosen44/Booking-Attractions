from sitemap_generator.city_sitemap_builder import CitySitemapBuilder
from sitemap_generator.config import SitemapConfig
from sitemap_generator.postgres_reader import SitemapPostgresReader
from sitemap_generator.property_sitemap_builder import PropertySitemapBuilder
from sitemap_generator.sitemap_index_builder import SitemapIndexBuilder
from sitemap_generator.writer import SitemapWriter


# Generates all sitemap files plus the master index
class SitemapGenerationRunner:
    def run(self):
        filenames = []
        filenames.extend(self._write_property_sitemaps())
        filenames.append(self._write_city_sitemap())
        self._write_index(filenames)

        print(f"Generated {len(filenames)} sitemap files in {SitemapConfig.OUTPUT_DIR}")

    def _write_property_sitemaps(self) -> list:
        print("Building property sitemaps...")
        filenames = []
        part = 1
        buffer = []

        for batch in SitemapPostgresReader.iter_property_batches(1000):
            buffer.extend(batch)
            while len(buffer) >= SitemapConfig.URLS_PER_FILE:
                chunk, buffer = buffer[:SitemapConfig.URLS_PER_FILE], buffer[SitemapConfig.URLS_PER_FILE:]
                filenames.append(self._write_property_chunk(chunk, part))
                part += 1

        if buffer:
            filenames.append(self._write_property_chunk(buffer, part))

        return filenames

    @staticmethod
    def _write_property_chunk(rows: list, part: int) -> str:
        xml_content = PropertySitemapBuilder.build_urlset(rows)
        filename = f"property-sitemap-{part}"
        SitemapWriter.write(filename, xml_content)
        print(f"Wrote {filename} ({len(rows)} urls)")
        return filename

    @staticmethod
    def _write_city_sitemap() -> str:
        print("Building city sitemap...")
        groups = SitemapPostgresReader.city_groups()
        xml_content = CitySitemapBuilder.build_urlset(groups)
        filename = "city-sitemap"
        SitemapWriter.write(filename, xml_content)
        print(f"Wrote {filename} ({len(groups)} cities)")
        return filename

    @staticmethod
    def _write_index(filenames: list):
        xml_content = SitemapIndexBuilder.build(filenames)
        SitemapWriter.write("site-map-all", xml_content)
        print("Wrote site-map-all")
