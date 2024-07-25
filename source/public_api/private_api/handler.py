import mimetypes

import httpx
from fastapi import Response, UploadFile
from loguru import logger
from pydantic import BaseModel

from http_exceptions import HTTPObjectNotExist, HTTPPrivatePostFailed
from settings import settings
from types_ import ID_TYPE

async_client = httpx.AsyncClient()


def private_route_v1(endpoint, path: str = ''):
    route = \
        settings.HTTP_PROTOCOL + '://' + \
        settings.PRIVATE_API_HOST + ':' + \
        settings.PRIVATE_API_PORT + '/' + \
        settings.PRIVATE_API_V1 + \
        endpoint
    if path:
        route += f'/{path}'
    return route


class Endpoints(BaseModel):
    post_memes: str = '/files'
    delete_memes_by_id: str = '/files'
    get_url_by_id: str = '/files/get_url'


endpoints = Endpoints()


async def post_upload_file(file: UploadFile, media_type: str) \
        -> httpx.Response:
    try:
        async with httpx.AsyncClient() as client:
            response_from_priv_api = await client.post(
                private_route_v1(endpoints.post_memes),
                files={'file': (file.filename, file.file)},
                headers={'Media-type': media_type})
    except httpx.WriteTimeout:
        logger.opt(exception=True).error('Sending to private API timeout')
        raise HTTPPrivatePostFailed
    except httpx.ReadTimeout:
        logger.opt(exception=True).error(
            'Request response from private API timeout')
        raise HTTPPrivatePostFailed
    except Exception as error:
        logger.opt(exception=True).error('Error on post to private api')
    else:
        return response_from_priv_api
    return httpx.Response(status_code=httpx.codes.INTERNAL_SERVER_ERROR)


async def get_presigned_url(meme_data: dict, url: str) -> str:
    body_data = {'expires': settings.PRESIGNED_URL_EXPIRE_TIME,
                 'media_type': mimetypes.types_map[meme_data.extension],
                 'extension': meme_data.extension}
    response_url = await async_client.get(url, params=body_data)
    presigned_url = response_url.text
    if not presigned_url:
        logger.opt(exception=True).error('None url returned by private api.')
        raise HTTPObjectNotExist
    return presigned_url


async def get_image_with_url(url: str) -> Response:
    private_request = async_client.build_request('GET', url['url'])
    private_response = await async_client.send(private_request, stream=True)
    return private_response


async def delete_image_from_s3(id: ID_TYPE):
    url = private_route_v1(endpoints.delete_memes_by_id, str(id))
    try:
        async with httpx.AsyncClient() as client:
            private_response = await client.delete(url)
    except httpx.WriteTimeout:
        logger.opt(exception=True).error('Sending to private API timeout')
        raise HTTPPrivatePostFailed
    except httpx.ReadTimeout:
        logger.opt(exception=True).error(
            'Request response from private API timeout')
        raise HTTPPrivatePostFailed
    return private_response
