import mimetypes
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import httpx
import jwt
from loguru import logger

from http_exceptions import HTTPTokenExpiredError
from private_api.handler import endpoints, private_route_v1
from schemas.image_base import MemeBaseSchema, MemeBaseSchemaOut
from settings import settings
from types_ import ID_TYPE


def get_meme_data(meme: MemeBaseSchema,
                  filename: str,
                  id: ID_TYPE | None = None) -> dict:
    image_id = uuid4() if not id else id
    meme_data = meme.model_dump()
    extension = os.path.splitext(filename)[-1].lower()
    meme_data['id'] = image_id
    meme_data['extension'] = extension
    meme_data['media_type'] = mimetypes.types_map[extension]
    return meme_data


def get_meme_data_url(meme: dict) -> tuple[MemeBaseSchemaOut, httpx.URL]:
    meme_data = MemeBaseSchemaOut.model_validate(meme)
    extension = meme_data.extension
    filename = str(meme_data.id)
    endpoint = private_route_v1(endpoints.get_url_by_id)
    url = httpx.URL(endpoint + '/' + filename)
    return meme_data, str(url)


def get_tokenized_public_url(presigned_url: str) -> httpx.URL:
    jwt_expire_time = datetime.now(tz=timezone.utc) + \
        timedelta(seconds=settings.PRESIGNED_URL_EXPIRE_TIME)
    private_url = jwt.encode(
        {'exp': jwt_expire_time,
         'url': presigned_url},
        key=settings.JWT_TOKEN_URL_SECRET,
        algorithm=settings.JWT_TOKEN_ALGO)
    url = url_concatenate(private_url)
    public_url = httpx.URL(url)
    return public_url, private_url


def url_concatenate(private_url: str) -> str:
    url = settings.HTTP_PROTOCOL + '://' + \
        settings.HTTP_HOST + \
        ((':' + str(settings.HTTP_PORT)) if settings.HTTP_PORT else '') + \
        '/' + \
        settings.PRIVATE_API_V1 + '/' + \
        'memes' + '/' + \
        'get_image' + '/' +\
        private_url
    return url


def decode_jwt_url(token):
    try:
        url = jwt.decode(token, key=settings.JWT_TOKEN_URL_SECRET,
                         algorithms=[settings.JWT_TOKEN_ALGO,])
    except jwt.exceptions.ExpiredSignatureError:
        logger.debug('Signature expired')
        raise HTTPTokenExpiredError
    except jwt.exceptions.DecodeError:
        logger.debug('Not enough segments jwd decode')
        raise
    return url
