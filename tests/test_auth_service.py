import pytest

pytest_plugins = ('pytest_asyncio',)

from apps.auth.requests import LoginRequest
from apps.auth.user.requests import CreateUserRequest

from services.exceptions import EmailExistsException, UsernameExistsException

import uuid # for random username/email generation

from services.auth import AuthService

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

# TODO: USE SETUP AND TEARDOWN FOR CLEANUP

@pytest.mark.asyncio(loop_scope="session")
async def test_hashing():
    password = "qwe123qwe123"

    hashed_password = AuthService._hash_password(password)

    assert password != hashed_password
    assert AuthService.verify_password(password, hashed_password)
    assert not AuthService.verify_password(password+"qwewqew", hashed_password)
    assert not AuthService.verify_password(password, password)
    assert not AuthService.verify_password(hashed_password, hashed_password)

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user():
    user_repo = await RepositoryFactory.get_repository(UserRepository)
    random_username = uuid.uuid4().hex.replace('-','_')
    random_email = f"{random_username}@testmail.com"
    password = "112233"

    create_request = CreateUserRequest(
        username=random_username,
        email=random_email,
        password=password,
    )

    random_user = await AuthService.create_user(create_request)

    assert random_user is not None
    assert random_user.password != password
    assert AuthService.verify_password(password, random_user.password)

    random_username_2 = uuid.uuid4().hex.replace('-','_')
    random_email_2 = f"{random_username_2}@testmail.com"
    password_2 = "11223344"

    create_dup_username = CreateUserRequest(
        username=random_username,
        email=random_email_2,
        password=password_2,
    )

    try:
        dup_username_user = await AuthService.create_user(create_dup_username) # should raise exception here
        await user_repo.delete(dup_username_user)
        assert False
    except UsernameExistsException:
        assert True

    create_dup_email = CreateUserRequest(
        username=random_username_2,
        email=random_email,
        password=password_2,
    )

    try:
        dup_email_user = await AuthService.create_user(create_dup_email) # should raise exception here
        await user_repo.delete(dup_email_user)
        assert False
    except EmailExistsException:
        assert True

    # cleanup
    await user_repo.delete(random_user)

@pytest.mark.asyncio(loop_scope="session")
async def test_token():
    user_repo = await RepositoryFactory.get_repository(UserRepository)

    test_user = await user_repo.get_all().first_or_none()
    user_token = AuthService.create_token(test_user)
    token_data = AuthService.decode_token(user_token.token)

    assert token_data.user_id == test_user.id

@pytest.mark.asyncio(loop_scope="session")
async def test_login():
    user_repo = await RepositoryFactory.get_repository(UserRepository)

    random_username = uuid.uuid4().hex.replace('-','_')
    random_email = f"{random_username}@testmail.com"
    password = "112233"

    create_request = CreateUserRequest(
        username=random_username,
        email=random_email,
        password=password,
    )

    test_user = await AuthService.create_user(create_request)

    login_request = LoginRequest(
        usernameOrEmail = test_user.email,
        password = password,
    )

    login_response = await AuthService.login(login_request)

    user_token_data = AuthService.decode_token(login_response.token)

    assert test_user.id == user_token_data.user_id

    # cleanup
    await user_repo.delete(test_user)
