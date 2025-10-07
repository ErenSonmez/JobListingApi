import os
import asyncio

from beanie import init_beanie, Document
import pkgutil
import importlib
import inspect

from typing import Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository
from repositories.schemas import MongoClientCredentials
from repositories.exceptions import RepositoryNotFoundException

from repositories.utils import validate_and_create_mongo_credentials

_REPO_TYPE = TypeVar("_REPO_TYPE", bound=BaseRepository)

class RepositoryFactory:
    _CREDENTIALS: MongoClientCredentials = None

    ENV_DB_HOST_KEY = "MONGO_HOST"
    ENV_DB_PORT_KEY = "MONGO_PORT"

    ENV_DB_USERNAME_KEY = "MONGO_ADMIN_USER"
    ENV_DB_PASSWORD_KEY = "MONGO_ADMIN_PASS"

    ENV_DB_NAME_KEY = "DB_NAME"

    _DB_CLIENT: AsyncIOMotorClient = None

    _INSTANCES: dict[str,object] = {}

    @classmethod
    def _get_credentials_from_env(cls):
        host = os.getenv(cls.ENV_DB_HOST_KEY)
        port = os.getenv(cls.ENV_DB_PORT_KEY)

        username = os.getenv(cls.ENV_DB_USERNAME_KEY)
        password = os.getenv(cls.ENV_DB_PASSWORD_KEY)

        db_name = os.getenv(cls.ENV_DB_NAME_KEY)

        creds = validate_and_create_mongo_credentials(host, port, username, password, db_name)

        return creds

    @classmethod
    def _create_client(cls):
        if cls._CREDENTIALS is None:
            cls._CREDENTIALS = cls._get_credentials_from_env()

        creds = cls._CREDENTIALS

        cls._DB_CLIENT = AsyncIOMotorClient(f'mongodb://{creds.username}:{creds.password}@{creds.host}:{creds.port}/')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(cls._init_odm())

    @classmethod
    async def _init_odm(cls):
        import models

        model_classes = []
        for module_info in pkgutil.iter_modules(models.__path__):
            module = importlib.import_module(f"models.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Document) and obj is not Document:
                    model_classes.append(obj)

        await init_beanie(
            database=cls._DB_CLIENT.get_database(cls._CREDENTIALS.db_name),
            document_models=model_classes,
        )

    @classmethod
    def _get_client(cls):
        if cls._DB_CLIENT is None:
            cls._create_client()

        return cls._DB_CLIENT

    @classmethod
    def set_db_credentials(cls, creds: MongoClientCredentials, create_client: bool = True):
        cls._CREDENTIALS = validate_and_create_mongo_credentials(creds.host, creds.port, creds.username, creds.password, creds.db_name)

        cls._DB_CLIENT = None
        if create_client:
            cls._create_client()



    @classmethod
    def get_repository(cls, repo_type: Type[_REPO_TYPE]) -> _REPO_TYPE:
        repo_name = repo_type.__name__

        if repo_name in cls._INSTANCES:
            return cls._INSTANCES[repo_name]

        if not issubclass(repo_type, BaseRepository):
            raise RepositoryNotFoundException(repo_type)

        client = cls._get_client()

        cls._INSTANCES[repo_name] = repo_type(client)
        return cls._INSTANCES[repo_name]
