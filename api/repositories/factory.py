import os

import beanie
from beanie import Document

import pkgutil
import importlib
import inspect

from typing import Type, TypeVar

from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository
from repositories.schemas import MongoClientCredentials
from repositories.exceptions import RepositoryNotFoundException

_REPO_TYPE = TypeVar("_REPO_TYPE", bound=BaseRepository)

class RepositoryFactory:
    _CREDENTIALS: MongoClientCredentials = None

    ENV_DB_HOST_KEY = "MONGO_HOST"
    ENV_DB_PORT_KEY = "MONGO_PORT"

    ENV_DB_USERNAME_KEY = "MONGO_ADMIN_USER"
    ENV_DB_PASSWORD_KEY = "MONGO_ADMIN_PASS"

    ENV_DB_NAME_KEY = "DB_NAME"

    _DB_CLIENT: AsyncIOMotorClient = None

    _MODEL_CLASSES: list[Document] = None

    _INSTANCES: dict[str,object] = {}

    @classmethod
    async def _get_credentials_from_env(cls):
        host = os.getenv(cls.ENV_DB_HOST_KEY)
        port = os.getenv(cls.ENV_DB_PORT_KEY)

        username = os.getenv(cls.ENV_DB_USERNAME_KEY)
        password = os.getenv(cls.ENV_DB_PASSWORD_KEY)

        db_name = os.getenv(cls.ENV_DB_NAME_KEY)

        creds = MongoClientCredentials(
            host = host,
            port = port,
            username = username,
            password = password,
            db_name = db_name
        )

        return creds

    @classmethod
    async def _get_credentials(cls):
        if cls._CREDENTIALS is None:
            cls._CREDENTIALS = await cls._get_credentials_from_env()

        return cls._CREDENTIALS

    @classmethod
    async def _set_model_classes(cls):
        import models

        model_classes = []
        for module_info in pkgutil.iter_modules(models.__path__):
            module = importlib.import_module(f"models.{module_info.name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Document) and obj is not Document:
                    model_classes.append(obj)

        cls._MODEL_CLASSES = model_classes

    @classmethod
    async def _get_model_classes(cls):
        if cls._MODEL_CLASSES is None:
            await cls._set_model_classes()

        return cls._MODEL_CLASSES

    @classmethod
    async def _init_odm(cls, reset_model_classes: bool = False):
        if reset_model_classes:
            await cls._set_model_classes()

        model_classes = await cls._get_model_classes()

        await beanie.init_beanie(
            database=cls._DB_CLIENT.get_database(cls._CREDENTIALS.db_name),
            document_models = model_classes,
        )

    @classmethod
    async def _create_client(cls):
        creds = await cls._get_credentials()

        cls._DB_CLIENT = AsyncIOMotorClient(
            f'mongodb://{creds.username}:{creds.password}@{creds.host}:{creds.port}/',
            maxPoolSize = 20,
            minPoolSize = 1,
        )

        await cls._init_odm(reset_model_classes=True)

    @classmethod
    async def _get_client(cls):
        if cls._DB_CLIENT is None:
            await cls._create_client()

        return cls._DB_CLIENT

    @classmethod
    async def _create_repository(cls, repo_type: Type[_REPO_TYPE]) -> _REPO_TYPE:
        if not issubclass(repo_type, BaseRepository):
            raise RepositoryNotFoundException(repo_type)

        client = await cls._get_client()
        return repo_type(client)

    @classmethod
    async def set_db_credentials(cls, creds: MongoClientCredentials, create_client: bool = True):
        cls._CREDENTIALS = creds

        cls._DB_CLIENT = None
        if create_client:
            await cls._create_client()

    @classmethod
    async def setup(cls):
        await cls._create_client()

    @classmethod
    async def teardown(cls):
        pass # TODO: Teardown DB setup

    @classmethod
    async def get_repository(cls, repo_type: Type[_REPO_TYPE], reset_repo: bool = False) -> _REPO_TYPE:
        repo_name = repo_type.__name__

        if not reset_repo and repo_name in cls._INSTANCES:
            return cls._INSTANCES[repo_name]

        repo = await cls._create_repository(repo_type)
        cls._INSTANCES[repo_name] = repo

        return repo
