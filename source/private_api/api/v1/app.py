from fastapi import FastAPI

from api.v1.endpoints.files import router_files
from settings import settings

tags_metadata = [
    {
        'name': 'v1',
        'description': 'Private API version 1',
        'externalDocs': {
            'description': 'sub-docs',
            'url': f'http://{settings.HTTP_HOST}' +
                (f':{settings.HTTP_PORT}/' if settings.HTTP_PORT else '/') +
                f'{settings.V1}/docs'
        }
    },
]

app = FastAPI(openapi_tags=tags_metadata)
app.include_router(router_files)
