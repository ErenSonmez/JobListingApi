from typing import Any
from beanie import PydanticObjectId
import pytest

pytest_plugins = ('pytest_asyncio',)

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserData

@pytest.mark.asyncio(loop_scope="session")
async def test_repository_crud():
    assert 1==1

    test_user_data = UserData(
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
    update_user_data = UserData(
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

    fetch_update_users = await repo.find(User.username == update_user_model_with_id.username)
    fetch_update_user = None
    for u in fetch_update_users:
        if u.id == update_user_model_with_id.id:
            fetch_update_user = u
            break
    assert fetch_update_user is not None
    assert fetch_update_user.id == update_user_model_with_id.id
    assert fetch_update_user.username == update_user_model_with_id.username
