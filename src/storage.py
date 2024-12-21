import os
from datetime import datetime, timedelta

import boto3

from config import Config
from logger import log_json


class StorageBase:
    def upload_image(self, filename, img_bytes):
        raise NotImplementedError()

    def get_image_access(self, filename):
        """
        Return either a local file path (file mode) or a pre-signed URL (s3 mode).
        """
        raise NotImplementedError()


class S3Storage(StorageBase):
    def __init__(self):
        if Config.S3_ENDPOINT:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=Config.S3_ACCESS_KEY,
                aws_secret_access_key=Config.S3_SECRET_KEY,
                endpoint_url=Config.S3_ENDPOINT,
            )
        else:
            self.client = boto3.client(
                "s3",
                aws_access_key_id=Config.S3_ACCESS_KEY,
                aws_secret_access_key=Config.S3_SECRET_KEY,
            )
        self._ensure_bucket()

    def _ensure_bucket(self):
        buckets = self.client.list_buckets()
        bucket_names = [b["Name"] for b in buckets["Buckets"]]
        if Config.S3_BUCKET_NAME not in bucket_names:
            self.client.create_bucket(Bucket=Config.S3_BUCKET_NAME)
            log_json(20, "Created S3 bucket", bucket=Config.S3_BUCKET_NAME)

    def upload_image(self, filename, img_bytes):
        # PNG instead of JPG
        self.client.put_object(
            Bucket=Config.S3_BUCKET_NAME, Key=filename, Body=img_bytes, ContentType="image/png"
        )
        log_json(20, "Image uploaded to S3", objectName=filename)

    def get_image_access(self, filename):
        # Generate a pre-signed URL valid for (e.g. 1 hour)
        url = self.client.generate_presigned_url(
            "get_object", Params={"Bucket": Config.S3_BUCKET_NAME, "Key": filename}, ExpiresIn=3600
        )
        return url


class FileStorage(StorageBase):
    def __init__(self):
        self.path = Config.FILE_STORAGE_PATH
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
            log_json(20, "Created local directory for images", directory=self.path)

    def upload_image(self, filename, img_bytes):
        full_path = os.path.join(self.path, filename)
        with open(full_path, "wb") as f:
            f.write(img_bytes)
        log_json(20, "Image saved locally", path=full_path)

    def get_image_access(self, filename):
        # Return local file path
        return os.path.join(self.path, filename)


def get_storage():
    if Config.STORAGE_BACKEND == "file":
        return FileStorage()
    else:
        return S3Storage()
