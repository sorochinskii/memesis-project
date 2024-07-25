import sys
from dataclasses import asdict, dataclass
from os import getenv
from os.path import abspath, dirname

from dotenv import find_dotenv
from dump_env.dumper import dump
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

current_dir = dirname((abspath(__file__))) + '/'
sys.path.append(current_dir)

TEMPLATE_ENV_FILE: str = '.env.template'
PROD_ENV_FILE: str = '.env'
LOCAL_ENV_FILE: str = current_dir+'.local.env'
LOCAL_TEST_ENV_FILE: str = current_dir+'.local.testing.env'
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
    LOG_DIR: str = Field(default='logs')
    HTTP_PROTOCOL: str = Field(default='https')
    HTTP_PORT: int | None = Field(default=None)
    HTTP_HOST: str | None = Field(default='localhost')

    S3_BUCKET: str = Field()
    S3_ROOT_USER: str | None = Field(default=None)
    S3_ROOT_PASSWORD: str | None = Field(default=None)
    S3_USER: str = Field()
    S3_PASSWORD: str = Field()
    S3_USER_GROUP: str | None = Field(default=None)
    S3_HTTP_HOST: str = Field()
    S3_HTTP_PORT: str = Field()
    S3_HTTP_PROTOCOL: str = Field()
    S3_URL: str = Field()
    S3_ENDPOINT: str = Field()
    MAX_FILE_SIZE: int = Field()
    S3_SERVICE_NAME: str = Field()
    S3_CHUNK_LENGTH: int = Field()
    S3_USE_SSL: bool = Field()
    V1: str = Field()

    @model_validator(mode='after')
    def set_environment(self):
        env_vars = EnvironmentVars()
        assert self.ENVIRONMENT in asdict(env_vars).values(), \
            f'{self.ENVIRONMENT=} not in possible {asdict(env_vars).values()}'
        return self

    class Config:
        validate_assignment = True


settings = Settings(env_file=env_file)
