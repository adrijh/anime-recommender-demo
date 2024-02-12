import os

IS_LOCAL = os.getenv("IS_LOCAL", "false").lower() == "true"
BUCKET_NAME = os.environ["BUCKET_NAME"]
OPENSEARCH_ENDPOINT = os.environ["OPENSEARCH_ENDPOINT"]
INDEX_ALIAS = os.environ["INDEX_ALIAS"]
