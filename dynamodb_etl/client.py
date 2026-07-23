import boto3

from dynamodb_etl.config import DynamoConfig


# Singleton resource, dummy creds for local endpoint
class DynamoClient:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = boto3.resource(
                "dynamodb",
                endpoint_url=DynamoConfig.ENDPOINT_URL,
                region_name=DynamoConfig.REGION,
                aws_access_key_id="local",
                aws_secret_access_key="local",
            )
        return cls._instance
