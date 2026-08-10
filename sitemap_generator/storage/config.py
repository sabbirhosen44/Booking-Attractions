from core.configuration import S3


class S3Config:
    ENDPOINT_URL = S3.get("endpoint_url")
    REGION = S3.get("region", "us-east-1")
    BUCKET = S3.get("bucket")
    PREFIX = S3.get("prefix", "")
    ACCESS_KEY = S3.get("access_key")
    SECRET_KEY = S3.get("secret_key")