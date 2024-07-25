import json
from typing import Any

from pydantic import Field, HttpUrl, field_validator, model_validator

from logger_config import logger
from schemas.base import BaseSchema
from types_ import ID_TYPE

extensions = ['.jpg', '.png', '.jpeg']


class MemeBaseSchema(BaseSchema):
    name: str = Field(..., max_length=10)
    text: str | None = Field(None, max_length=100)

    class Config:
        from_attributes = True
        # validate_assignment = True

    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value: Any) -> Any:
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class MemesBaseListSchema(BaseSchema):
    memes: list[MemeBaseSchema]


class MemeSchemaOut(MemeBaseSchema):
    url: HttpUrl
    token: str


class MemeBaseSchemaOut(MemeBaseSchema):
    extension: str
    id: ID_TYPE

    @field_validator('extension')
    def check_extension(cls, v: str) -> str:
        if v not in extensions:
            logger.opt(exception=True).debug('')
            raise ValueError('Wrong extension')
        return v

    class Config:
        from_attributes = True
