import json

import f_indexer.config as cfg
from f_indexer.namespace import AnimeRecord
from f_indexer.opensearch import OpenSearchHelper
from f_indexer.source import S3Source


def transform_to_records(data: list[dict]) -> list[AnimeRecord]:
    print("Transforming records...")
    return [
        AnimeRecord(
            anime_id=record["id"],
            title=record.get("title"),
            title_en=record.get("alternative_titles", {}).get("en"),
            main_picture=record.get("main_picture", {}).get("medium"),
            start_date=record.get("start_date"),
            end_date=record.get("end_date"),
            synopsis=record.get("synopsis"),
            mean=float(record.get("mean", 0)),
            rank=int(record.get("rank", 0)),
            popularity=int(record.get("popularity", 0)),
            num_list_users=int(record.get("num_list_users", 0)),
            num_scoring_users=int(record.get("num_scoring_users", 0)),
        )
        for record in data
        if record.get("synopsis")
    ]

def main(event: dict):
    if not event.get("Records"):
        print("Not S3 trigger event, exiting...")
        return

    print("Creating helper...")
    source = S3Source(cfg.BUCKET_NAME)
    os_helper = OpenSearchHelper()

    print("Start processing records..")
    anime_details = []
    for record in event["Records"]:
        message_body = json.loads(record['body'])
        for s3_event in message_body['Records']:
            object_key = s3_event['s3']['object']['key']
            processed = transform_to_records(source.read(object_key))
            anime_details.extend(processed)

    response = os_helper.bulk_with_retry(anime_details)
    print(response)
