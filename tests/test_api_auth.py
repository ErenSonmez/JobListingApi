import pytest
import logging

pytest_plugins = ('pytest_asyncio',)


from models.user import UserDataPublic

from apps.auth.responses import LoginResponse
from apps.auth.user.requests import CreateUserRequest
from apps.auth.requests import LoginRequest

from services.auth import AuthService

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

import uuid # for random username/email generation

import aiohttp

@pytest.mark.asyncio(loop_scope="session")
async def test_authorize_and_send_request():
    random_username = uuid.uuid4().hex.replace('-','_')
    random_email = f"{random_username}@testmail.com"
    password = "112233"

    create_request = CreateUserRequest(
        username=random_username,
        email=random_email,
        password=password,
    )

    random_user = await AuthService.create_user(create_request)

    logging.info(f"random_user: {random_user.model_dump_json()}")

    base_url = "http://127.0.0.1:8000/"

    async with aiohttp.ClientSession(base_url=base_url) as session:
        login_url = "/api/auth/login"
        login_request = LoginRequest(
            usernameOrEmail = random_user.email,
            password = password
        )
        logging.info(f"login_request {login_request.model_dump_json()}")

        login_response = await session.post(login_url, json=login_request.model_dump())
        login_response_json = await login_response.json()
        logging.info(f"login_response_json {login_response_json}")
        login_response = LoginResponse.model_validate(login_response_json)

        token = login_response.token.token

        current_user_url = "/api/auth/user/me"
        current_user_response = await session.get(current_user_url, headers={"Authorization": f"Bearer {token}"})
        assert current_user_response.status == 200

        current_user_data = UserDataPublic.model_validate(await current_user_response.json())

        assert current_user_data.email == random_user.email
        assert current_user_data.username == random_user.username
