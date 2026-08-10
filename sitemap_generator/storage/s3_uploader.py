from pathlib import Path

import boto3

from sitemap_generator.storage.config import S3Config


class S3Uploader:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=S3Config.ENDPOINT_URL,
            region_name=S3Config.REGION,
            aws_access_key_id=S3Config.ACCESS_KEY,
            aws_secret_access_key=S3Config.SECRET_KEY,
        )

    def upload(self, local_path: str | Path, object_key: str) -> None:
        self.client.upload_file(
            str(local_path),
            S3Config.BUCKET,
            object_key,
        )

        print(
            f"Uploaded {local_path} "
            f"to s3://{S3Config.BUCKET}/{object_key}"
        )