import os

from api.v1.app import app as app_v1
from fastapi import FastAPI
from settings import settings

app = FastAPI(title='Private API for memesis.')
app.mount('/v1', app_v1)

current_dir = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app_main',
                host=f'{settings.HTTP_HOST}',
                port=settings.HTTP_PORT,
                reload=True,
                reload_dirs=[current_dir],
                log_level='debug')
