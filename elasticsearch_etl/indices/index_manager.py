from elasticsearch_etl.config import ESConfig
from elasticsearch_etl.indices.mappings import INDEX_MAPPINGS


# Creates indices if missing, does not migrate existing ones
class IndexManager:
    @staticmethod
    def create_indices_if_not_exist(client) -> None:
        for table_name, mapping in INDEX_MAPPINGS.items():
            index_name = ESConfig.index(table_name)
            if not client.indices.exists(index=index_name):
                client.indices.create(index=index_name, mappings=mapping)
                print(f"Created index: {index_name}")
            else:
                print(f"Already exists: {index_name}")
