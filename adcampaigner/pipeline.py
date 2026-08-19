import json

from adcampaigner.config import AdCampaignerConfig
from adcampaigner.postgres_reader import PostgresPropertyReader

from adcampaigner.transformers.location_mapper import LocationMapper
from adcampaigner.transformers.price_segment import (
    PriceSegmentTransformer,
)
from adcampaigner.transformers.property_score import (
    PropertyScoreTransformer,
)
from adcampaigner.transformers.property_transformer import (
    PropertyTransformer,
)

from adcampaigner.builders.custom_label_builder import (
    CustomLabelBuilder,
)
from adcampaigner.builders.feed_row_builder import (
    FeedRowBuilder,
)
from adcampaigner.builders.page_url_builder import (
    PageUrlBuilder,
)
from adcampaigner.builders.remarketing_row_builder import (
    RemarketingRowBuilder,
)

from adcampaigner.writers.csv_writer import CsvWriter
from adcampaigner.writers.remarketing_csv_writer import (
    RemarketingCsvWriter,
)
from adcampaigner.writers.html_index_writer import (
    HtmlIndexWriter,
)


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

        self.reader = (
            PostgresPropertyReader()
        )

        self.property_transformer = (
            PropertyTransformer()
        )

        self.price_segment = (
            PriceSegmentTransformer()
        )

        self.location_mapper = LocationMapper(
            AdCampaignerConfig.COUNTRY_MAP_FILE,
            AdCampaignerConfig.TIER_REGION_CONTINENT_MAP_FILE,
        )

        self.property_score = (
            PropertyScoreTransformer(
                self._load_price_scores()
            )
        )

        self.url_builder = PageUrlBuilder(
            AdCampaignerConfig.SITE_URL
        )

        self.label_builder = (
            CustomLabelBuilder()
        )

        self.row_builder = (
            FeedRowBuilder()
        )

        self.remarketing_builder = (
            RemarketingRowBuilder()
        )

        self.csv_writer = CsvWriter(
            AdCampaignerConfig.OUTPUT_DIR,
            AdCampaignerConfig.MAX_ROWS_PER_FILE,
        )

        self.remarketing_writer = (
            RemarketingCsvWriter(
                AdCampaignerConfig.OUTPUT_DIR,
                AdCampaignerConfig.MAX_ROWS_PER_FILE,
            )
        )

        self.html_writer = (
            HtmlIndexWriter()
        )

    def run(self):
        page_feed_writers = {}
        page_feed_entries = []

        self.remarketing_writer.start()

        try:
            for property_data in self.reader.read():
                row, remarketing_row = (
                    self._build_rows(
                        property_data
                    )
                )

                if row is not None:
                    continent = row.pop(
                        "_continent"
                    )

                    writer = (
                        page_feed_writers.get(
                            continent
                        )
                    )

                    if writer is None:
                        writer = (
                            self._create_continent_writer(
                                continent
                            )
                        )

                        if writer is None:
                            continue

                        page_feed_writers[
                            continent
                        ] = writer

                    writer.write_row(row)

                if remarketing_row is not None:
                    self.remarketing_writer.write_row(
                        remarketing_row
                    )

        finally:
            for (
                continent,
                writer,
            ) in page_feed_writers.items():
                page_feed_entries.extend(
                    writer.finish()
                )

            remarketing_feed_entries = (
                self.remarketing_writer.finish()
            )

        feed_entries = self._build_feed_entries(
            page_feed_entries,
            remarketing_feed_entries,
        )

        self.html_writer.write(
            feed_entries
        )

        print(
            f"Generated "
            f"{len(page_feed_entries)} "
            f"page feed files and "
            f"{len(remarketing_feed_entries)} "
            f"remarketing feed files "
            f"in "
            f"{AdCampaignerConfig.OUTPUT_DIR}"
        )

        return feed_entries

    def _create_continent_writer(
        self,
        continent,
    ):
        continent_name = (
            self.CONTINENT_FILE_MAP.get(
                continent
            )
        )

        if not continent_name:
            return None

        filename = (
            f"{AdCampaignerConfig.FILE_PREFIX}_"
            f"{continent_name}.csv"
        )

        writer = CsvWriter(
            AdCampaignerConfig.OUTPUT_DIR,
            AdCampaignerConfig.MAX_ROWS_PER_FILE,
        )

        writer.start(filename)

        return writer

    @staticmethod
    def _build_feed_entries(
        page_feed_entries,
        remarketing_feed_entries,
    ):
        feed_entries = [
            (
                filename,
                AdCampaignerConfig.PAGE_CAMPAIGN_TYPE,
                count,
            )
            for filename, count
            in page_feed_entries
        ]

        feed_entries.extend(
            (
                filename,
                AdCampaignerConfig.REMARKETING_CAMPAIGN_TYPE,
                count,
            )
            for filename, count
            in remarketing_feed_entries
        )

        return feed_entries

    def _build_rows(
        self,
        property_data,
    ):
        property_data = (
            self.property_transformer.transform(
                property_data
            )
        )

        location = (
            self.location_mapper.transform(
                property_data.get(
                    "country_code"
                )
            )
        )

        continent = location.get(
            "continent"
        )

        if (
            not continent
            or continent == "void"
        ):
            return None, None

        page_url = (
            self.url_builder.build(
                property_data
            )
        )

        if (
            not page_url
            or page_url == "void"
        ):
            return None, None

        price = property_data.get(
            "usd_price"
        )

        price_segment = (
            self.price_segment.transform(
                price
            )
        )

        property_score = (
            self.property_score.transform(
                price
            )
        )

        custom_label = (
            self.label_builder.build(
                city=property_data.get(
                    "city"
                ),
                country=location.get(
                    "country"
                ),
                property_type=(
                    AdCampaignerConfig
                    .PROPERTY_TYPE
                ),
                price_segment=price_segment,
                price=price,
                property_score=property_score,
                continent=continent,
                tier=location.get(
                    "tier"
                ),
                region=location.get(
                    "region"
                ),
            )
        )

        row = self.row_builder.build(
            page_url,
            custom_label,
        )

        row["_continent"] = continent

        remarketing_row = (
            self.remarketing_builder.build(
                property_data,
                location,
                page_url,
                property_score,
            )
        )

        return row, remarketing_row

    @staticmethod
    def _load_price_scores():
        with (
            AdCampaignerConfig
            .PRICE_SCORE_PERCENTILES_FILE
            .open(
                "r",
                encoding="utf-8",
            )
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return next(
                iter(data.values())
            )

        raise ValueError(
            "Invalid price score percentile data."
        )