from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from logger_config import logger
from settings import settings
from v1.endpoints.memes import router_memes

tags_metadata = [
    {
        'name': 'v1',
        "description": "Public API version 1",
        'externalDocs': {
            'description': 'sub-docs',
            'url': f'http://{settings.HTTP_HOST}' +
                (f':{settings.HTTP_PORT}/' if settings.HTTP_PORT else '/') +
                f'{settings.V1}/docs'
        }
    },
]


app = FastAPI(openapi_tags=tags_metadata)
app.include_router(router_memes)
