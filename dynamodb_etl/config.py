from pathlib import Path

from core.configuration import BASE_DIR, DYNAMODB, IMPORT

PACKAGE_DIR = Path(__file__).resolve().parent


# DynamoDB connection settings, local docker only
class DynamoConfig:
    DATA_DIR = Path(BASE_DIR) / IMPORT["data_dir"]
    ENDPOINT_URL = DYNAMODB["endpoint_url"]
    REGION = DYNAMODB.get("region", "us-east-1")
    BATCH_SIZE = 25
