from elasticsearch import Elasticsearch

from elasticsearch_etl.config import ESConfig


# Singleton ES client for local docker instance
class ESClient:
    _instance = None

    @classmethod
    def get(cls) -> Elasticsearch:
        if cls._instance is None:
            cls._instance = Elasticsearch(
                ESConfig.HOST,
                request_timeout=60,
                max_retries=3,
                retry_on_timeout=True,
            )
        return cls._instance
