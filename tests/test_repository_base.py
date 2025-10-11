import pytest

pytest_plugins = ('pytest_asyncio',)

import importlib
import inspect
import pkgutil

from repositories.factory import RepositoryFactory
from repositories.base import BaseRepository
from repositories.schemas import MongoClientCredentials

def get_repository_classes() -> list[BaseRepository]:
    import repositories

    repository_classes = []
    for module_info in pkgutil.iter_modules(repositories.__path__):
        module = importlib.import_module(f"src.repositories.{module_info.name}")

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseRepository) and obj is not BaseRepository:
                repository_classes.append(obj)

    return repository_classes

repo_classes = get_repository_classes()

def test_get_repository_classes():
    assert len(repo_classes)>0
    assert all([issubclass(rc, BaseRepository) for rc in repo_classes])

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'repo_class',
    repo_classes,
    ids = lambda cls: cls.__name__    ,
)
async def test_repository_client(repo_class):
    db_client = await RepositoryFactory._get_client()
    repo: BaseRepository = await RepositoryFactory.get_repository(repo_class)
    assert db_client is repo._client

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'repo_class',
    repo_classes,
    ids = lambda cls: cls.__name__    ,
)
async def test_repository_type(repo_class):
    repo: BaseRepository = await RepositoryFactory.get_repository(repo_class)
    assert isinstance(repo, repo_class)

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'repo_class',
    repo_classes,
    ids = lambda cls: cls.__name__    ,
)
async def test_repository_cache(repo_class):
    first_repo: BaseRepository = await RepositoryFactory.get_repository(repo_class)
    second_repo: BaseRepository = await RepositoryFactory.get_repository(repo_class)
    assert first_repo is second_repo

@pytest.mark.asyncio(loop_scope="session")
async def test_repository_model_cache():
    first_models = await RepositoryFactory._get_model_classes()
    second_models = await RepositoryFactory._get_model_classes()
    assert first_models is second_models

@pytest.mark.asyncio(loop_scope="session")
async def test_repository_reset():
    first_creds = await RepositoryFactory._get_credentials()
    first_client = await RepositoryFactory._get_client()

    new_creds = MongoClientCredentials(
        host = first_creds.host,
        port = first_creds.port,
        username = first_creds.username,
        password = first_creds.password,
        db_name = first_creds.db_name,
    )

    await RepositoryFactory.set_db_credentials(new_creds)

    second_creds = await RepositoryFactory._get_credentials()
    second_client = await RepositoryFactory._get_client()

    assert second_creds is new_creds
    assert first_creds is not second_creds
    assert first_client is not second_client

    new_creds = MongoClientCredentials(
        host = first_creds.host,
        port = first_creds.port,
        username = first_creds.username,
        password = first_creds.password,
        db_name = first_creds.db_name,
    )

    await RepositoryFactory.set_db_credentials(new_creds, False)

    third_creds = await RepositoryFactory._get_credentials()

    assert third_creds is new_creds
    assert second_creds is not third_creds
    assert RepositoryFactory._DB_CLIENT is None

    third_client = await RepositoryFactory._get_client()

    assert RepositoryFactory._DB_CLIENT is third_client
    assert third_client is not second_client
