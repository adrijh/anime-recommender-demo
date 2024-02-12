import json
import os
from datetime import datetime
from typing import Protocol

import boto3
from mypy_boto3_s3.client import S3Client

from f_poller.namespace import PollingSpec


class Sink(Protocol):
    def save(self, data: list[dict], spec: PollingSpec) -> None:
        ...

class S3Sink:
    def __init__(
        self,
        bucket_name: str,
        client: S3Client | None = None
    ):
        self.bucket_name = bucket_name
        self.client = client if client else boto3.client("s3")
        self.current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.prefix = f"mal_{self.current_timestamp}"

    def save(self, data: list[dict], spec: PollingSpec) -> None:
        filepath = f"{self.prefix}/{spec.year}_{spec.season_name}_{spec.current_page}.json"

        newline_json = '\n'.join(json.dumps(record) for record in data)
        self.client.put_object(
            Body=newline_json,
            Bucket=self.bucket_name,
            Key=filepath,
        )

class FileSystemSink:
    def __init__(
        self,
        data_folder: str,
    ):
        self.data_folder = data_folder
        self.current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.prefix = f"mal_{self.current_timestamp}"

    def save(self, data: list[dict], spec: PollingSpec) -> None:
        filepath = os.path.join(
            self.data_folder,
            self.prefix,
            f"{spec.year}_{spec.season_name}_{spec.current_page}.json",
        )

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            for record in data:
                f.write(json.dumps(record) + "\n")
