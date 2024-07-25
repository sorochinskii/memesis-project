from psycopg2 import errorcodes
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from logger_config import logger


class ItemNotFound(SQLAlchemyError):
    ...


class ItemNotUnique(SQLAlchemyError):
    ...


class ErrorHandler:

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_instance, traceback):
        if hasattr(ex_instance, 'orig'):
            match ex_instance.orig.pgcode:
                case errorcodes.UNIQUE_VIOLATION:
                    raise ItemNotUnique('Not unique')
                case errorcodes.FOREIGN_KEY_VIOLATION:
                    raise SQLAlchemyError('Foreign key not present')
        elif ex_type == NoResultFound:
            logger.debug('No result found', ex_instance)
            raise ItemNotFound
        elif ex_type == ConnectionRefusedError:
            logger.critical(ConnectionRefusedError(
                'No connection to database'))
            raise ConnectionRefusedError
        elif ex_instance:
            raise ex_instance
