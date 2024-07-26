import asyncio
import os
from typing import AsyncIterator

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from main import app
from PIL import Image
from pydantic import BaseModel
from settings import settings
from testcontainers.postgres import PostgresContainer

postgres = PostgresContainer('postgres:15.6-alpine3.19',
                             driver='asyncpg',
                             username=settings.DB_USER,
                             password=settings.DB_PASS,
                             dbname=settings.DB_NAME).with_bind_ports(
                                 container=settings.DB_PORT_CONTAINER,
                                 host=settings.DB_PORT)


def run_migrations(dsn: str) -> None:
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', 'migration')
    alembic_cfg.set_main_option('sqlalchemy.url', dsn)
    command.upgrade(alembic_cfg, 'head')


@pytest.fixture(scope='session')
def event_loop(request):
    '''Для решения проблемы ScopeMismatch: "You tried to access
    the 'function' scoped fixture 'event_loop' with a 'module'
    scoped request object, involved factories."
    Create an instance of the default event loop for each test case.'''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class Image(BaseModel):
    name: str
    size: tuple
    mode: str = 'RGB'


class Meme(BaseModel):
    name: str
    text: str | None = None


@pytest.fixture
async def test_client() -> AsyncIterator[AsyncClient]:
    url = settings.HTTP_PROTOCOL + '://' + settings.HTTP_HOST
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url=url) as client:
        yield client


@pytest.fixture(scope='session', autouse=True)
def setup():
    pytest.filename_1 = 'image_1.jpg'
    pytest.filename_2 = 'image_2.png'
    pytest.files = [pytest.filename_1, pytest.filename_2]
    pytest.image_1 = Image(name=pytest.filename_1, size=(200, 200))
    pytest.image_2 = Image(name=pytest.filename_2, size=(300, 300))
    pytest.meme_1 = Meme(name='Some meme', text='Your meme is mine')
    pytest.meme_2 = Meme(name='Other meme')
    db = postgres.start()
    run_migrations(settings.DB_URL)


def pytest_sessionfinish(session, exitstatus):
    postgres.stop()
    for file in pytest.files:
        try:
            os.remove(file)
        except:
            ...
