import gzip

from sitemap_generator.config import SitemapConfig


# Writes sitemap XML content to disk, gzip optional to mirror rentbyowner's .gz files
class SitemapWriter:
    @staticmethod
    def write(filename: str, xml_content: str) -> str:
        SitemapConfig.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        if SitemapConfig.GZIP_OUTPUT:
            path = SitemapConfig.OUTPUT_DIR / f"{filename}.xml.gz"
            with gzip.open(path, "wt", encoding="utf-8") as f:
                f.write(xml_content)
        else:
            path = SitemapConfig.OUTPUT_DIR / f"{filename}.xml"
            with open(path, "w", encoding="utf-8") as f:
                f.write(xml_content)

        return str(path)
