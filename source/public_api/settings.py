import sys
from dataclasses import asdict, dataclass
from os import getenv
from os.path import abspath, dirname

from dotenv import find_dotenv
from dump_env.dumper import dump
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

current_dir = dirname((abspath(__file__)))+'/'
sys.path.append(current_dir)
TEMPLATE_ENV_FILE: str = '.env.template'
PROD_ENV_FILE: str = '.env'
LOCAL_ENV_FILE: str = current_dir+'.local.env'
LOCAL_TEST_ENV_FILE: str = current_dir+'.testing.env'
TEST_ENV_FILE: str = '.testing.env'
SOURCE_ENV: str = '.env'

ENVIRONMENT: str | None = getenv('ENVIRONMENT')


@dataclass
class EnvironmentVars:
    prod: str = 'prod'
    local: str = 'local'
    local_testing: str = 'local_testing'
    testing: str = 'testing'


match ENVIRONMENT:
    case EnvironmentVars.prod:
        env_file = find_dotenv(PROD_ENV_FILE, raise_error_if_not_found=True)
    case EnvironmentVars.testing:
        env_file = find_dotenv(TEST_ENV_FILE, raise_error_if_not_found=True)
    case EnvironmentVars.local:
        env_file = find_dotenv(LOCAL_ENV_FILE, raise_error_if_not_found=True)
    case EnvironmentVars.local_testing:
        env_file = find_dotenv(LOCAL_TEST_ENV_FILE,
                               raise_error_if_not_found=True)
    case _:
        raise Exception('Dot env file not found')


class Settings(BaseSettings):
    def __init__(self, env_file):
        super().__init__(_env_file=env_file, _case_sensitive=True, )
    ENVIRONMENT: str = Field(default='ENVIRONMENT')
    DB_HOST: str = Field(default='DB_HOST')
    DB_PASS: str = Field(default='DB_PASS')
    DB_PORT: str = Field()
    DB_PORT_CONTAINER: str = Field()
    DB_USER: str = Field(default='DB_USER')
    DB_NAME: str = Field(default='DB_NAME')
    DB_URL: str = Field(default='DB_URL')
    POSTGRES_PASSWORD: str = Field(default='POSTGRES_PASSWORD')
    POSTGRES_USER: str = Field(default='POSTGRES_USER')
    POSTGRES_DB: str = Field(default='POSTGRES_DB')
    LOG_DIR: str = Field(default='logs')
    SECRET: str = Field(default='SECRET')
    TEMPLATES_DIR: str = Field(default='source/templates')
    TEMPLATE_VERIFICATION: str = Field(default='email_verification.html')
    HTTP_PROTOCOL: str = Field(default='https')
    HTTP_PORT: int = Field(default=80)
    HTTP_HOST: str = Field()
    UPLOAD_IMAGE_SIZE: int = Field(default=1048576)
    PRIVATE_API_HOST: str = Field('localhost')
    PRIVATE_API_PORT: str = Field('8002')
    PRIVATE_API_V1: str = Field('v1')
    MAX_IMAGE_SIZE: int = Field()
    EXIF_REMOVE: int | None = Field(default=None)
    JWT_TOKEN_URL_SECRET: str = Field()
    JWT_TOKEN_ALGO: str = Field()
    PRESIGNED_URL_EXPIRE_TIME: int = Field()
    V1: str = Field()

    @model_validator(mode='before')
    def get_database_url(cls, values):
        values['DB_URL'] = (
            f'postgresql+asyncpg://{values["DB_USER"]}:{values["DB_PASS"]}'
            + f'@{values["DB_HOST"]}:{values["DB_PORT"]}/{values["DB_NAME"]}'
        )
        return values

    @model_validator(mode='after')
    def set_environment(self):
        env_vars = EnvironmentVars()
        assert self.ENVIRONMENT in asdict(env_vars).values(), \
            f'{self.ENVIRONMENT=} not in possible {asdict(env_vars).values()}'
        return self

    class Config:
        validate_assignment = True


settings = Settings(env_file=env_file)
