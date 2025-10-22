import pytest_asyncio

import logging
import uuid

from beanie import PydanticObjectId

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserDataFull

def generate_random_user_data(username: str = None, password: str = None, email: str = None,
                              username_prefix: str = "", email_prefix: str = ""):
    if not username:
        username = uuid.uuid4().hex

    if not password:
        password = uuid.uuid4().hex

    if not email:
        email = f"{username}@testmail.com"

    if username_prefix:
        username = f"{username_prefix}{username}"

    if email_prefix:
        email = f"{email_prefix}{email}"

    return UserDataFull(
        username = username,
        password = password,
        email = email,
    )

@pytest_asyncio.fixture(scope="session")
async def setup_teardown_users():
    logging.info("setup_teardown_users setup start")
    users_to_delete: list[User] = []
    user_ids_to_delete: list[PydanticObjectId] = []

    logging.info("setup_teardown_users setup end")
    yield users_to_delete, user_ids_to_delete

    logging.info("setup_teardown_users teardown start")
    user_repo = await RepositoryFactory.get_repository(UserRepository)
    for user in users_to_delete:
        if user is not None:
            logging.info(f"setup_teardown_users teardown deleting user {user}")
            await user_repo.delete(user)

    for user_id in user_ids_to_delete:
        if user_id is not None:
            logging.info(f"setup_teardown_users teardown deleting user with id {user_id}")
            await user_repo.delete(user_id)
    logging.info("setup_teardown_users teardown end")
