from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from settings import settings

engine = create_async_engine(settings.DB_URL)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator:
    async with async_session_maker() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
