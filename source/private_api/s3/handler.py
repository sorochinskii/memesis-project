import typing
from uuid import uuid4

import botocore
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi import status
from urllib3.exceptions import MaxRetryError

from logger_config import logger
from settings import settings


class S3Handler:

    def __init__(self,
                 bucket: str,
                 secure: bool = False):
        self.bucket = bucket

    def rename_s3_object(self,
                         client: typing.Type[BaseClient],
                         old_name: str,
                         new_name: str) -> str:
        try:
            client.copy_object(Bucket=self.bucket,
                               CopySource=f'{self.bucket}/{old_name}',
                               Key=new_name)
        except ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchKey':
                logger.opt(exception=True).error('Non existent s3 object key')
                raise error
        client.delete_object(Bucket=self.bucket, Key=old_name)
        return new_name

    def check_connection(self, client: typing.Type[BaseClient]):
        fake_bucket_name = str(uuid4())
        try:
            client.bucket_exists(fake_bucket_name)
        except MaxRetryError as e:
            logger.critical(e)
            raise e
        except ConnectionRefusedError as e:
            logger.critical(e)
            raise e
        return True

    def get_presigned_url(self,
                          name: str,
                          extension: str,
                          client: typing.Type[BaseClient],
                          expires: int | None,
                          media_type: str) -> str | None:
        try:
            client.head_object(Bucket=self.bucket, Key=name)
        except ClientError as e:
            logger.opt(exception=True).error(e)
            return None
        resource = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket,
                    'Key': name,
                    'ResponseContentType': media_type,
                    'ResponseContentDisposition':
                        'inline'},
            # f"attachment; filename = {name}{extension}"},
            ExpiresIn=expires)
        return resource

    def get(self, name: str, client: typing.Type[BaseClient]):
        info = client.stat_object(self.bucket, name)
        total_size = info.size
        offset = 0
        while True:
            response = client.get_object(
                bucket_name=self.bucket,
                object_name=name,
                offset=offset,
                length=settings.S3_CHUNK_LENGTH)
            yield response.read()
            offset = offset + settings.S3_CHUNK_LENGTH
            if offset >= total_size:
                break

    def delete_file(self,
                    name: str,
                    client: typing.Type[BaseClient]):
        if self.key_exist(name, client=client):
            client.delete_object(Bucket=self.bucket, Key=name)
            return True

    def key_exist(self, name, client: typing.Type[BaseClient]):
        try:
            client.head_object(Bucket=self.bucket,
                               Key=name)
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == \
                    str(status.HTTP_404_NOT_FOUND):
                return False
            else:
                logger.opt(exception=True).error('Non existent s3 key')
                raise error
        return True


s3_handler = S3Handler(bucket=settings.S3_BUCKET)
