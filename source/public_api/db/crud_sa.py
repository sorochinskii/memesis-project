from typing import Any, Sequence, Type

from loguru import logger
from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from db.exception_handler import ErrorHandler
from db.models.base import BaseCommon
from types_ import ID_TYPE

MODEL_TYPE = Type[BaseCommon]


class CRUDSA:

    def __init__(
            self,
            model: MODEL_TYPE,
            *args: Any,
            **kwargs: Any
    ):
        self.model = model

    async def get_all(self,
                      session: AsyncSession,
                      skip: int = 0,
                      paginate: int = 0) -> Sequence[Any]:
        stmt = select(self.model).offset(skip).fetch(paginate)
        async with session as session:
            with ErrorHandler() as error_handler:
                raw = await session.scalars(stmt)
                result = raw.unique().all()
        return result

    async def get_all_with_related(self,
                                   session: AsyncSession) -> Sequence[Any]:
        stmt = select(self.model
                      ).order_by(
            getattr(self.model, self.model.get_pks()[0]))
        async with session as session:
            with ErrorHandler() as error_handler:
                raw = await session.scalars(stmt)
                result = raw.unique().all()
        return result

    async def get_by_id(self,
                        id: ID_TYPE,
                        session: AsyncSession):
        stmt = select(self.model
                      ).filter_by(id=id)
        async with session as session:
            with ErrorHandler() as error_handler:
                result = await session.scalar(stmt)
        return result

    async def get_all_with_filters(self,
                                   session: AsyncSession,
                                   filter: dict,
                                   skip: int = 0,
                                   paginate: int = 0) -> DeclarativeBase:
        stmt = select(self.model
                      ).offset(skip).fetch(paginate).filter_by(**filter)
        async with session:
            with ErrorHandler() as error_handler:
                raw = await session.scalars(stmt)
                result = raw.unique().all()
        return result

    async def create(self,
                     data: dict,
                     session: AsyncSession) -> DeclarativeBase:
        stmt = insert(self.model).returning(self.model)
        async with session:
            with ErrorHandler():
                result = await session.scalar(stmt, [data])
                await session.commit()
        logger.debug(f'SA crud create statement: {stmt}, data: {data}')
        return result

    async def update(self, id: ID_TYPE,
                     data: dict,
                     session: AsyncSession) -> DeclarativeBase:
        stmt = update(self.model).\
            where(self.model.id == id).\
            values(data).\
            returning(self.model)
        async with session:
            with ErrorHandler():
                result = await session.scalar(stmt)
                await session.commit()
        return result

    async def delete(self, item_id: ID_TYPE, session: AsyncSession) -> \
            int | None:
        stmt = delete(self.model).\
            where(self.model.id == item_id).\
            returning(self.model.id)
        with ErrorHandler():
            await self.check_exist_by_id(item_id, session)
        async with session:
            result = await session.scalar(stmt)
            await session.commit()
        return result

    async def check_exist_by_id(self, id, session):
        query = text(
            f'SELECT * FROM {self.model.__tablename__} WHERE id=:id')
        async with session:
            result = await session.execute(query, {'id': id})
        return result.one()
