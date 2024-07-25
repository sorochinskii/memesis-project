import os

from fastapi import FastAPI

from settings import settings
from v1.app import app as app_v1

app = FastAPI(title='Public API for memesis.')
app.mount('/v1', app_v1)


current_dir = os.path.dirname(os.path.realpath(__file__))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app',
                host=f'{settings.HTTP_HOST}',
                port=settings.HTTP_PORT,
                reload=True,
                reload_dirs=[current_dir],
                log_level='debug')
