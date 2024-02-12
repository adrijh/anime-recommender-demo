import json
from typing import Protocol

import boto3
from mypy_boto3_s3.client import S3Client


class Source(Protocol):
    def read(self, path: str):
        ...

class S3Source:
    def __init__(
        self,
        bucket_name: str,
        client: S3Client | None = None
    ):
        self.bucket_name = bucket_name
        self.client = client if client else boto3.client("s3")

    def read(self, path: str) -> list[dict]:
        obj = self.client.get_object(Bucket=self.bucket_name, Key=path)
        obj_decoded = obj['Body'].read().decode('utf-8')
        data = map(
            lambda x: json.loads(x),
            obj_decoded.splitlines(),
        )
        return list(data)

class FileSystemSource:
    def read(self, path: str) -> list[dict]:
        data = []
        with open(path) as f:
            for line in f:
                data.append(json.loads(line))

        return data
