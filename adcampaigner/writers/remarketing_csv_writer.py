from pathlib import Path

from adcampaigner.writers.csv_writer import CsvWriter
from adcampaigner.config import AdCampaignerConfig


class RemarketingCsvWriter(CsvWriter):

    HEADERS = [
        "Property ID",
        "Property Name",
        "Final URL",
        "Image URL",
        "Destination Name",
        "Description",
        "Price",
        "Star Rating",
        "Category",
    ]

    FIELD_KEYS = [
        "property_id",
        "property_name",
        "final_url",
        "image_url",
        "destination_name",
        "description",
        "price",
        "star_rating",
        "category",
    ]

    def write(self, rows) -> list[str]:
        rows = list(rows)

        if not rows:
            return []

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        files = []
        total_rows = len(rows)

        for start in range(
            0,
            total_rows,
            self.max_rows_per_file,
        ):
            chunk = rows[
                start:start + self.max_rows_per_file
            ]

            part = start // self.max_rows_per_file + 1

            output_filename = (
                AdCampaignerConfig.get_remarketing_file_name(part)
            )

            output_path = self.output_dir / output_filename

            self._write_file(
                output_path,
                chunk,
            )

            files.append(output_filename)

        return files