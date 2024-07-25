from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import S3Target
from streaming_form_data.validators import MaxSizeValidator, ValidationError

from dependencies.s3 import get_s3_client
from http_exceptions import (
    HTTPCommonUploadException,
    HTTPFileIsMissing,
    HTTPFileSizeLimitException,
    HTTPObjectNotExist,
)
from logger_config import logger
from s3.handler import s3_handler
from settings import settings
from utils import s3_file_path

router_files = APIRouter(
    prefix='/files',
    tags=['files']
)


@router_files.get('/{id}', response_class=StreamingResponse)
async def get_file(id: str, client=Depends(get_s3_client)):
    file = s3_handler.get(id, client=client)
    if file:
        return StreamingResponse(file['Body'].iter_chunks())
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Item not found'
        )


@ router_files.get('/get_url/{id}', response_class=Response)
async def get_url(id: str,
                  extension: str,
                  media_type: str,
                  expires: int | None = None,
                  client=Depends(get_s3_client)):
    file_url = s3_handler.get_presigned_url(name=id,
                                            extension=extension,
                                            expires=expires,
                                            media_type=media_type,
                                            client=client,)
    return file_url


@router_files.post('', status_code=status.HTTP_201_CREATED, response_class=StreamingResponse)
async def upload(request: Request,
                 client=Depends(get_s3_client)) -> str:
    parser = StreamingFormDataParser(headers=request.headers)
    fake_filename = str(uuid4())
    max_size_validator = MaxSizeValidator(settings.MAX_FILE_SIZE)
    s3_file = s3_file_path(fake_filename)
    s3_target = S3Target(s3_file, mode='wb',
                         transport_params={'client': client},
                         validator=max_size_validator)
    parser.register('file', s3_target)
    try:
        async for chunk in request.stream():
            parser.data_received(chunk)
        if s3_target.multipart_filename:
            new_object_name = s3_handler.rename_s3_object(
                client,
                fake_filename,
                s3_target.multipart_filename)
        else:
            raise HTTPFileIsMissing
    except ValidationError:
        logger.opt(exception=True).error(
            'Max size validator error.')
        raise HTTPFileSizeLimitException
    except Exception as e:
        logger.opt(exception=True).error('Common exception problems')
        raise HTTPCommonUploadException
    return new_object_name


@router_files.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete(id: str, client=Depends(get_s3_client)):
    result = s3_handler.delete_file(name=id, client=client)
    if not result:
        raise HTTPObjectNotExist
    return result
