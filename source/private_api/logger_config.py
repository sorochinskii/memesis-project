import sys

from loguru import logger
from settings import ENVIRONMENT, settings

format = '{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message} | {extra}'
if ENVIRONMENT != 'prod':
    DEBUG_SINK = f'{settings.LOG_DIR}/debug/' + '{time:YYYY_MM_DD}'
    INFO_SINK = f'{settings.LOG_DIR}/info/' + '{time:YYYY_MM_DD}'
    ERROR_SINK = f'{settings.LOG_DIR}/error/' + '{time:YYYY_MM_DD}'
    CRITICAL_SINK = f'{settings.LOG_DIR}/critical/' + '{time:YYYY_MM_DD}'
else:
    DEBUG_SINK = INFO_SINK = ERROR_SINK = CRITICAL_SINK = sys.stderr

logger.remove()


logger.add(DEBUG_SINK,
           filter=lambda record: record['level'].name == 'DEBUG',
           format=format)

logger.add(INFO_SINK,
           filter=lambda record: record['level'].name == 'INFO',
           format=format)

logger.add(ERROR_SINK,
           filter=lambda record: record['level'].name == 'ERROR',
           format=format)

logger.add(CRITICAL_SINK,
           filter=lambda record: record['level'].name == 'CRITICAL',
           format=format)
