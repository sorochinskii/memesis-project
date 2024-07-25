from fastapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    File,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse

from db.crud_sa import CRUDSA
from db.db import get_async_session
from db.models.memes import Memes
from file_helpers.remove_exif import remove_exif
from http_exceptions import HTTPObjectNotExist, HTTPPrivatePostFailed
from logger_config import logger
from private_api.handler import (
    delete_image_from_s3,
    get_image_with_url,
    get_presigned_url,
    post_upload_file,
)
from schemas.image_base import MemeBaseSchema, MemeBaseSchemaOut, MemeSchemaOut
from settings import settings
from types_ import ID_TYPE
from validators import validate_content_type, validate_file_size

from .utils import (
    decode_jwt_url,
    get_meme_data,
    get_meme_data_url,
    get_tokenized_public_url,
)

router_memes = APIRouter(
    prefix='/memes',
    tags=['memes']
)
crud = CRUDSA(Memes)

app = FastAPI()


@router_memes.get('/{id}', response_model=MemeSchemaOut)
async def get_by_id(id: ID_TYPE,
                    session: AsyncSession = Depends(get_async_session)):
    meme = await crud.get_by_id(id, session)
    if not meme:
        raise HTTPObjectNotExist
    meme_data, url = get_meme_data_url(meme)
    presigned_url = await get_presigned_url(meme_data, url)
    public_url, private_url = get_tokenized_public_url(presigned_url)
    return {'name': meme_data.name,
            'text': meme_data.text,
            'url': str(public_url),
            'token': private_url}


@router_memes.get('/get_image/{token}', response_class=StreamingResponse)
async def get_image_by_token(token: str, request: Request):
    url = decode_jwt_url(token)
    private_response = await get_image_with_url(url)
    return StreamingResponse(
        private_response.aiter_raw(),
        status_code=private_response.status_code,
        headers=private_response.headers,
        background=BackgroundTask(private_response.aclose),
    )


@router_memes.post('', response_model=MemeBaseSchemaOut)
async def upload(meme: MemeBaseSchema = Body(...),
                 file: UploadFile = File(...),
                 session: AsyncSession = Depends(get_async_session)):
    validate_content_type(file)
    validate_file_size(file)
    meme_data = get_meme_data(meme, file.filename)
    file.filename = str(meme_data['id'])
    if settings.EXIF_REMOVE:
        file = remove_exif(file.file)
    response_from_priv_api = await post_upload_file(file,
                                                    meme_data['media_type'])
    if response_from_priv_api.status_code == status.HTTP_201_CREATED:
        await crud.create(meme_data, session=session)
        return meme_data
    else:
        logger.opt(exception=True).error(
            f'Sending to private API failed.')
        raise HTTPPrivatePostFailed


@router_memes.get('', status_code=status.HTTP_200_OK,
                  response_model=list[MemeBaseSchemaOut])
async def list_memes(page: int = Query(ge=0, default=1),
                     size: int = Query(ge=1, le=100, default=2),
                     session: AsyncSession = Depends(get_async_session)) \
        -> list[MemeBaseSchemaOut]:
    memes_from_db = await crud.get_all_with_filters(
        session=session,
        skip=page,
        paginate=size,
        filter={'delete_mark': False})
    return memes_from_db


@router_memes.delete('/{id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_meme(id: ID_TYPE,
                      session: AsyncSession = Depends(get_async_session)) \
        -> str:
    data = {'delete_mark': True}
    item = await crud.update(id=id, data=data, session=session)
    if not item:
        raise HTTPObjectNotExist
    image_id = str(item.id)
    respnose = await delete_image_from_s3(image_id)
    if not respnose.status_code == status.HTTP_200_OK:
        raise HTTPObjectNotExist
    return image_id


@router_memes.put('/{id}', status_code=status.HTTP_202_ACCEPTED,
                  response_model=MemeBaseSchemaOut)
async def replace_meme(id: ID_TYPE,
                       meme: MemeBaseSchema = Body(...),
                       file: UploadFile = File(...),
                       session: AsyncSession = Depends(get_async_session)):
    validate_content_type(file)
    validate_file_size(file)
    meme_data = get_meme_data(meme, file.filename, id)
    item = await crud.update(
        id=id,
        data=meme_data,
        session=session)
    if not item:
        raise HTTPObjectNotExist
    file.filename = str(id)
    await post_upload_file(file, meme_data['media_type'])
    return item
