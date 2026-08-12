from collections import defaultdict

from adcampaigner.config import AdCampaignerConfig
from adcampaigner.postgres_reader import PostgresPropertyReader
from adcampaigner.transformers.location_mapper import LocationMapper
from adcampaigner.transformers.price_segment import PriceSegmentTransformer
from adcampaigner.transformers.property_score import PropertyScoreTransformer
from adcampaigner.transformers.property_transformer import PropertyTransformer
from adcampaigner.builders.custom_label_builder import CustomLabelBuilder
from adcampaigner.builders.feed_row_builder import FeedRowBuilder
from adcampaigner.builders.page_url_builder import PageUrlBuilder
from adcampaigner.writers.csv_writer import CsvWriter
from adcampaigner.writers.html_index_writer import HtmlIndexWriter


class AdCampaignerGenerationRunner:

    CONTINENT_FILE_MAP = {
        "AFR": "afr",
        "AS": "as",
        "EUR": "eur",
        "NAM": "nam",
        "OC": "oc",
        "SAM": "sam",
    }

    def __init__(self):
        AdCampaignerConfig.validate()

        self.reader = PostgresPropertyReader()

        self.property_transformer = PropertyTransformer()
        self.price_segment = PriceSegmentTransformer()

        self.location_mapper = LocationMapper(
            AdCampaignerConfig.COUNTRY_MAP_FILE,
            AdCampaignerConfig.TIER_REGION_CONTINENT_MAP_FILE,
        )

        self.property_score = PropertyScoreTransformer(
            self._load_price_scores()
        )

        self.url_builder = PageUrlBuilder(
            AdCampaignerConfig.SITE_URL
        )

        self.label_builder = CustomLabelBuilder()
        self.row_builder = FeedRowBuilder()

        self.csv_writer = CsvWriter(
            AdCampaignerConfig.OUTPUT_DIR,
            AdCampaignerConfig.MAX_ROWS_PER_FILE,
        )

        self.html_writer = HtmlIndexWriter(
            AdCampaignerConfig.OUTPUT_DIR,
            AdCampaignerConfig.FEED_BASE_URL,
        )

    def run(self):
        rows_by_continent = defaultdict(list)

        for property_data in self.reader.read():
            row = self._build_row(property_data)

            if not row:
                continue

            continent = row.pop("_continent")

            rows_by_continent[continent].append(row)

            if len(rows_by_continent[continent]) >= (
                AdCampaignerConfig.MAX_ROWS_PER_FILE
            ):
                self._write_continent(
                    continent,
                    rows_by_continent[continent],
                )

                rows_by_continent[continent] = []

        feed_files = []

        for continent, rows in rows_by_continent.items():
            if rows:
                feed_files.extend(
                    self._write_continent(
                        continent,
                        rows,
                    )
                )

        feed_files.extend(
            self._collect_existing_feed_files()
        )

        feed_files = sorted(set(feed_files))

        self.html_writer.write(feed_files)

        print(
            f"Generated {len(feed_files)} feed files "
            f"in {AdCampaignerConfig.OUTPUT_DIR}"
        )

        return feed_files

    def _write_continent(self, continent, rows):
        continent_name = self.CONTINENT_FILE_MAP.get(
            continent
        )

        if not continent_name:
            return []

        filename = (
            f"{AdCampaignerConfig.FILE_PREFIX}_"
            f"{continent_name}.csv"
        )

        return self.csv_writer.write(
            rows,
            filename,
        )

    def _build_row(self, property_data):
        property_data = (
            self.property_transformer.transform(
                property_data
            )
        )

        location = self.location_mapper.transform(
            property_data.get("country_code")
        )

        continent = location.get("continent")

        if not continent:
            return None

        price = property_data.get("usd_price")

        price_segment = self.price_segment.transform(
            price
        )

        property_score = self.property_score.transform(
            price
        )

        page_url = self.url_builder.build(
            property_data
        )

        if not page_url:
            return None

        custom_label = self.label_builder.build(
            city=property_data.get("city"),
            country=location.get("country"),
            property_type=AdCampaignerConfig.PROPERTY_TYPE,
            price_segment=price_segment,
            price=price,
            property_score=property_score,
            continent=continent,
            tier=location.get("tier"),
            region=location.get("region"),
        )

        row = self.row_builder.build(
            page_url,
            custom_label,
        )

        row["_continent"] = continent

        return row

    def _collect_existing_feed_files(self):
        files = []

        for continent in AdCampaignerConfig.CONTINENT_CODES:
            prefix = (
                f"{AdCampaignerConfig.FILE_PREFIX}_"
                f"{continent}"
            )

            files.extend(
                path.name
                for path in (
                    AdCampaignerConfig.OUTPUT_DIR.glob(
                        f"{prefix}*.csv"
                    )
                )
            )

        return files

    @staticmethod
    def _load_price_scores():
        import json

        with AdCampaignerConfig.PRICE_SCORE_PERCENTILES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return next(iter(data.values()))

        raise ValueError(
            "Invalid price score percentile data."
        )