import os

os.environ["IS_LOCAL"] = "true"
os.environ["INDEX_ALIAS"] = "anime"
os.environ["BUCKET_NAME"] = "true"
os.environ["OPENSEARCH_ENDPOINT"] = "true"

from f_indexer.__main__ import transform_to_records
from f_indexer.opensearch import OpenSearchHelper
from f_indexer.source import FileSystemSource


data_path = os.path.join(os.path.dirname(__file__), "..", "data")


def main():
    source = FileSystemSource()
    os_helper = OpenSearchHelper()

    data = source.read(f"{data_path}/mal_20240219140028/2024_winter_0.json")
    processed = transform_to_records(data)
    os_helper.bulk_with_retry(processed)



if __name__ == "__main__":
    main()
