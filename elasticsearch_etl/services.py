from elasticsearch.helpers import bulk

from elasticsearch_etl.config import ESConfig


# Bulk indexes docs, upserts by id when given
class ESIndexService:
    def __init__(self, client):
        self.client = client

    def bulk_index(self, table_name: str, docs: list, id_field: str | None = None):
        if not docs:
            return 0, []

        index_name = ESConfig.index(table_name)
        actions = []
        for doc in docs:
            action = {"_index": index_name, "_source": doc}
            if id_field and doc.get(id_field):
                action["_id"] = doc[id_field]
            actions.append(action)

        return bulk(self.client, actions, stats_only=False, raise_on_error=False)
