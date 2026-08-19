from adcampaigner.config import AdCampaignerConfig
from adcampaigner.writers.csv_writer import CsvWriter


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

    def start(self) -> None:
        super().start(
            AdCampaignerConfig.get_remarketing_file_name()
        )