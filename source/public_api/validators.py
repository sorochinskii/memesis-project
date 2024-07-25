from enum import Enum
from tempfile import NamedTemporaryFile
from typing import IO

from starlette import status

from http_exceptions import (
    HTTPUnsupportedFileSize,
    HTTPUnsupportedFileType,
    HTTPUploadFileError,
)
from logger_config import logger
from settings import settings


class ImageTypes(str, Enum):
    jpg = 'image/jpg'
    jpeg = 'image/jpeg'
    png = 'image/png'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def validate_content_type(file):
    try:
        if file.content_type not in ImageTypes.list():
            logger.debug('Wrong file content type for upload')
            raise HTTPUnsupportedFileType
    except AttributeError:
        logger.debug('Upload file.content_type error')
        raise HTTPUploadFileError


def validate_file_size(file):
    real_file_size = 0
    temp: IO = NamedTemporaryFile(delete=True)
    for chunk in file.file:
        real_file_size += len(chunk)
        if real_file_size > settings.MAX_IMAGE_SIZE:
            raise HTTPUnsupportedFileSize
        temp.write(chunk)
    temp.close()
