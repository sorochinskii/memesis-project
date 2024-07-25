from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from db.models.utils import split_and_concatenate
from types_ import ID_TYPE


class Base(DeclarativeBase):
    ...


class TableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return split_and_concatenate(cls.__name__)


class IDUUIDMixin:
    __abstract__ = True

    id: Mapped[ID_TYPE] = mapped_column(primary_key=True, unique=True)


class BaseCommon(Base, TableNameMixin):
    __abstract__ = True

    class Config:
        from_attributes = True


created_at = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.now())
]


updated_at = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.now(),
                  onupdate=func.now())
]
