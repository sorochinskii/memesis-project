from contextlib import closing

import boto3

from settings import settings


def get_s3_client():
    with closing(
        boto3.client(
            service_name=settings.S3_SERVICE_NAME,
            aws_access_key_id=settings.S3_USER,
            aws_secret_access_key=settings.S3_PASSWORD,
            endpoint_url=settings.S3_URL,
            use_ssl=settings.S3_USE_SSL)) as client:
        yield client
