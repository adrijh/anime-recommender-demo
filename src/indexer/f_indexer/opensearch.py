from dataclasses import asdict

from opensearchpy import OpenSearch, Transport
from opensearchpy.helpers import bulk

import f_indexer.config as cfg
from f_indexer.namespace import AnimeRecord


class OpenSearchHelper:
    def __init__(self):
        self.client = self.__create_opensearch_client()
        self.index_alias = cfg.INDEX_ALIAS
        self.retry_attempts = 3
        self.chunk_size = 500
        self.timeout = 60

    def build_bulk_documents(self, records: list[AnimeRecord]) -> list[dict]:
        return [
            {
                "_index": cfg.INDEX_ALIAS,
                "_id": record.anime_id,
                "_source": asdict(record),
            }
            for record in records
        ]

    def bulk_with_retry(self, records: list[AnimeRecord]) -> dict[str, str]:
        print("Bulk indexing records...")
        bulk_documents = self.build_bulk_documents(records)
        response =  bulk(
            self.client,
            bulk_documents,
            max_retries=self.retry_attempts,
            chunk_size=self.chunk_size,
            timeout=self.timeout,
        )
        return response

    def __create_opensearch_client(self):
        if cfg.IS_LOCAL:
            hosts = [{"host": "localhost", "port": 9200}]
            options = dict(
                http_compress=True,
                use_ssl=True,
                verify_certs=False,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                http_auth=("admin", "admin"),
            )
        else:
            hosts = [{"host": cfg.OPENSEARCH_ENDPOINT, "port": 443}]
            options = dict(
                http_compress=True,
                use_ssl=True,
                verify_certs=True,
            )

        print(f"Creating OpenSearch connection with options {options} and host {hosts}")
        return OpenSearch(
            hosts=hosts,
            transport_class=Transport,
            **options,
        )
