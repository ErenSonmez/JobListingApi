import pytest

pytest_plugins = ('pytest_asyncio',)

import importlib
import inspect
import pkgutil

from beanie import PydanticObjectId

from typing import Any

from repositories.factory import RepositoryFactory
from repositories.base import BaseRepository
from repositories.schemas import MongoClientCredentials
from repositories.user import UserRepository

from models.user import User, UserDataFull

def get_repository_classes() -> list[BaseRepository]:
    import repositories

    repository_classes = []
    for module_info in pkgutil.iter_modules(repositories.__path__):
        module = importlib.import_module(f"repositories.{module_info.name}")

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

@pytest.mark.asyncio(loop_scope="session")
async def test_repository_crud():
    assert 1==1

    test_user_data = UserDataFull(
        username="test-data-username",
        password="test-data-password",
        email="test-data@email.com",
    )

    test_user_dict = {
        "username":"test-dict-username",
        "password":"test-dict-password",
        "email":"test-dict@email.com",
    }

    test_user_model = User(
        username="test-model-username",
        password="test-model-password",
        email="test-model@email.com",
    )

    repo = await RepositoryFactory.get_repository(UserRepository)

    new_user_data = await repo.create(test_user_data)
    new_user_dict = await repo.create(test_user_dict)
    new_user_model = await repo.create(test_user_model)

    assert new_user_data.id is not None
    assert new_user_dict.id is not None
    assert new_user_model.id is not None

    await repo.delete(new_user_data)
    await repo.delete(new_user_dict.id)

    fetch_new_user_data = await repo.get_by_id(new_user_data.id)
    fetch_new_user_dict = await repo.get_by_id(new_user_dict.id)

    assert fetch_new_user_data is None
    assert fetch_new_user_dict is None

    async def update_assert_statements(update_user_id: PydanticObjectId, old_data: dict[str, Any]):
        # assumes all fields are updated
        fetch_update_user_model = await repo.get_by_id(update_user_id)
        assert update_user_id == fetch_update_user_model.id
        assert old_data["username"] != fetch_update_user_model.username
        assert old_data["password"] != fetch_update_user_model.password
        assert old_data["email"] != fetch_update_user_model.email

    update_user_id = new_user_model.id

    old_data = new_user_model.model_dump()
    update_user_data = UserDataFull(
        username="update-test-data-username",
        password="update-test-data-password",
        email="update-test-data@email.com",
    )

    await repo.update(update_user_data, update_user_id)
    await update_assert_statements(update_user_id, old_data)

    update_user_dict = {
        "username":"update-test-dict-username",
        "password":"update-test-dict-password",
        "email":"update-test-dict@email.com",
    }
    old_data = update_user_data.model_dump()
    await repo.update(update_user_dict, update_user_id)
    await update_assert_statements(update_user_id, old_data)

    update_user_dict_with_id = {
        "_id": update_user_id,
        "username":"update-test-dict-with-id-username",
        "password":"update-test-dict-with-id-password",
        "email":"update-test-dict-with-id@email.com",
    }
    old_data = update_user_dict
    await repo.update(update_user_dict_with_id)
    await update_assert_statements(update_user_id, old_data)

    update_user_model = User(
        username="update-test-model-username",
        password="update-test-model-password",
        email="update-test-model@email.com",
    )
    old_data = update_user_dict_with_id
    await repo.update(update_user_model, update_user_id)
    await update_assert_statements(update_user_id, old_data)

    update_user_model_with_id = User(
        id=update_user_id,
        username="update-test-model-with-id-username",
        password="update-test-model-with-id-password",
        email="update-test-model-with-id@email.com",
    )
    old_data = update_user_model.model_dump()
    await repo.update(update_user_model_with_id)
    await update_assert_statements(update_user_id, old_data)

    fetch_update_users = repo.find(User.username == update_user_model_with_id.username)
    fetch_update_user = None
    async for u in fetch_update_users:
        if u.id == update_user_model_with_id.id:
            fetch_update_user = u
            break

    assert fetch_update_user is not None
    assert fetch_update_user.id == update_user_model_with_id.id
    assert fetch_update_user.username == update_user_model_with_id.username

    fetch_all_users = repo.get_all()
    user_count = await fetch_all_users.count()
    assert user_count >= 1 # there at least have to be one record on users.

    fetch_update_user = None
    async for u in fetch_all_users:
        if u.id == update_user_model_with_id.id:
            fetch_update_user = u
            break

    # get_all must include record we still didnt delete
    assert fetch_update_user is not None
    assert fetch_update_user.id == update_user_model_with_id.id
    assert fetch_update_user.username == update_user_model_with_id.username

    # cleanup
    await repo.delete(update_user_model_with_id)