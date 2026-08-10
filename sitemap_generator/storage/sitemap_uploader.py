from pathlib import Path

from sitemap_generator.config import SitemapConfig
from sitemap_generator.storage.config import S3Config
from sitemap_generator.storage.s3_uploader import S3Uploader


class SitemapUploader:

    def __init__(self):
        self.uploader = S3Uploader()

    def run(self):
        sitemap_files = self._get_sitemap_files()

        for sitemap_file in sitemap_files:
            object_key = self._build_object_key(sitemap_file)

            self.uploader.upload(
                local_path=sitemap_file,
                object_key=object_key,
            )

            print(
                f"Uploaded {sitemap_file.name} "
                f"to s3://{S3Config.BUCKET}/{object_key}"
            )

        print(f"Uploaded {len(sitemap_files)} sitemap files.")

    @staticmethod
    def _get_sitemap_files() -> list[Path]:
        output_dir = SitemapConfig.OUTPUT_DIR

        if not output_dir.exists():
            raise FileNotFoundError(
                f"Sitemap output directory does not exist: {output_dir}"
            )

        return sorted(output_dir.glob("*.xml.gz"))

    @staticmethod
    def _build_object_key(sitemap_file: Path) -> str:
        prefix = S3Config.PREFIX.strip("/")

        if prefix:
            return f"{prefix}/{sitemap_file.name}"

        return sitemap_file.name