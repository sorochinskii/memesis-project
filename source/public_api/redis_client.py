import sys

import redis.asyncio as redis

from logger_config import logger
from settings import settings


async def redis_connect() -> redis.Redis:
    try:
        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_USER_PASSWORD,
            username=settings.REDIS_USER,
            db=0,
            socket_timeout=5,
        )
        ping = await client.ping()
        if ping is True:
            yield client
    except redis.AuthenticationError:
        logger.critical("Redis authentication error.")
    except Exception as e:
        ...
    finally:
        await client.aclose()


client = redis_connect()
