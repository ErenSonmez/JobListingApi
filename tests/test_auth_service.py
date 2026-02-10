import pytest

import logging

pytest_plugins = ('pytest_asyncio',)

from apps.auth.requests import LoginRequest

from services.exceptions import EmailExistsException, UsernameExistsException

from services.auth import AuthService

from tests.utils import generate_random_user_data, setup_teardown_users

@pytest.mark.asyncio(loop_scope="session")
async def test_hashing_class():
    password = "qwe123qwe123"

    hashed_password = AuthService._hash_password(password)

    assert password != hashed_password
    assert AuthService.verify_password(password, hashed_password)
    assert not AuthService.verify_password(password+"qwewqew", hashed_password)
    assert not AuthService.verify_password(password, password)
    assert not AuthService.verify_password(hashed_password, hashed_password)

@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(setup_teardown_users):
    users_to_delete, user_ids_to_delete = setup_teardown_users

    random_user_data = generate_random_user_data(username_prefix="test_create_")
    random_user_create = await AuthService.create_user(random_user_data)
    users_to_delete.append(random_user_create)

    assert random_user_create is not None
    assert random_user_create.password != random_user_data.password
    assert AuthService.verify_password(random_user_data.password, random_user_create.password)

    logging.info(f"created random user {random_user_create}")

    dup_username_user_data = generate_random_user_data(username = random_user_data.username, email_prefix="test_create_dup_username_")

    try:
        dup_username_user_create = await AuthService.create_user(dup_username_user_data) # should raise exception here
        users_to_delete.append(dup_username_user_create)
        logging.error(f"created user with duplicate username: {dup_username_user_create}")
        assert False
    except UsernameExistsException:
        pass

    dup_email_user_data = generate_random_user_data(email = random_user_data.email, username_prefix="test_create_dup_email_")

    try:
        dup_email_user_create = await AuthService.create_user(dup_email_user_data) # should raise exception here
        users_to_delete.append(dup_email_user_create)
        logging.error(f"created user with duplicate email: {dup_email_user_create}")
        assert False
    except EmailExistsException:
        pass

@pytest.mark.asyncio(loop_scope="session")
async def test_token(setup_teardown_users):
    users_to_delete, user_ids_to_delete = setup_teardown_users

    random_user_data = generate_random_user_data(username_prefix="test_token_")
    random_user = await AuthService.create_user(random_user_data)
    users_to_delete.append(random_user)

    user_token_data = AuthService.create_token(random_user)
    token_data = AuthService.decode_token(user_token_data.token)

    assert token_data.user_id == random_user.id

@pytest.mark.asyncio(loop_scope="session")
async def test_login(setup_teardown_users):
    users_to_delete, user_ids_to_delete = setup_teardown_users

    random_user_data = generate_random_user_data(username_prefix="login_test_user_")
    random_user = await AuthService.create_user(random_user_data)
    users_to_delete.append(random_user)

    login_request = LoginRequest(
        usernameOrEmail = random_user.email,
        password = random_user_data.password,
    )

    login_response = await AuthService.login(login_request)
    user_token_data = AuthService.decode_token(login_response.token)

    assert random_user.id == user_token_data.user_id
