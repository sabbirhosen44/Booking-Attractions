from sitemap_generator.config import SitemapConfig
from sitemap_generator.postgres_reader import SitemapPostgresReader
from sitemap_generator.property_sitemap_builder import PropertySitemapBuilder
from sitemap_generator.sitemap_index_builder import SitemapIndexBuilder
from sitemap_generator.writer import SitemapWriter

# Small safety margin for the xml header and closing tag
WRAPPER_OVERHEAD_BYTES = 300


# Generates property sitemap, nearby property sitemap and sitemap index
class SitemapGenerationRunner:
    def run(self):
        filenames = []
        filenames.extend(self._write_chunked_sitemap(
            "property-sitemap", self._property_rows()
        ))
        filenames.extend(self._write_chunked_sitemap(
            "nearby-property-sitemap", self._nearby_rows()
        ))

        self._write_index(filenames)
        print(f"Generated {len(filenames)} sitemap files in {SitemapConfig.OUTPUT_DIR}")

    @staticmethod
    def _property_rows():
        for batch in SitemapPostgresReader.iter_property_batches(SitemapConfig.BATCH_SIZE):
            yield from batch

    @staticmethod
    def _nearby_rows():
        for batch in SitemapPostgresReader.iter_nearby_property_batches(
            SitemapConfig.BATCH_SIZE, SitemapConfig.NEARBY_RADIUS_KM
        ):
            yield from batch

    def _write_chunked_sitemap(self, base_filename: str, rows) -> list[str]:
        print(f"Building {base_filename}...")

        max_bytes = SitemapConfig.MAX_FILE_SIZE_MB * 1024 * 1024
        filenames = []
        part = 1
        buffer_blocks = []
        buffer_size = 0
        buffer_count = 0

        for row in rows:
            block = PropertySitemapBuilder.build_url_block(row)
            block_size = len(block.encode("utf-8"))

            would_exceed_count = buffer_count + 1 > SitemapConfig.MAX_URLS_PER_FILE
            would_exceed_size = buffer_size + block_size + WRAPPER_OVERHEAD_BYTES > max_bytes

            if buffer_blocks and (would_exceed_count or would_exceed_size):
                filenames.append(self._flush(base_filename, part, buffer_blocks))
                part += 1
                buffer_blocks, buffer_size, buffer_count = [], 0, 0

            buffer_blocks.append(block)
            buffer_size += block_size
            buffer_count += 1

        if buffer_blocks:
            filenames.append(self._flush(base_filename, part, buffer_blocks))

        return filenames

    @staticmethod
    def _flush(base_filename: str, part: int, blocks: list[str]) -> str:
        xml_content = PropertySitemapBuilder.wrap_urlset("".join(blocks))
        filename = base_filename if part == 1 else f"{base_filename}-{part}"

        SitemapWriter.write(filename, xml_content)
        print(f"Wrote {filename} ({len(blocks)} urls)")
        return filename

    @staticmethod
    def _write_index(filenames: list[str]):
        xml_content = SitemapIndexBuilder.build(filenames)
        SitemapWriter.write("site-map-all", xml_content)
        print("Wrote site-map-all")