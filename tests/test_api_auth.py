import pytest

pytest_plugins = ('pytest_asyncio',)


from models.user import UserDataPublic

from apps.auth.responses import LoginResponse
from apps.auth.requests import LoginRequest

from services.auth import AuthService

import aiohttp

from tests.utils import generate_random_user_data, setup_teardown_users

@pytest.mark.asyncio(loop_scope="session")
async def test_authorize_and_send_request(setup_teardown_users):
    users_to_delete, user_ids_to_delete = setup_teardown_users

    random_user_data = generate_random_user_data(username_prefix="test_authorize_and_send_request_user_")
    random_user = await AuthService.create_user(random_user_data)
    users_to_delete.append(random_user)

    base_url = "http://127.0.0.1:8000/"

    async with aiohttp.ClientSession(base_url=base_url) as session:
        login_url = "/api/auth/login"
        login_request = LoginRequest(
            usernameOrEmail = random_user.email,
            password = random_user_data.password
        )

        login_response = await session.post(login_url, json=login_request.model_dump())
        login_response_json = await login_response.json()
        login_response = LoginResponse.model_validate(login_response_json)

        token = login_response.token.token

        current_user_url = "/api/auth/user/me"
        current_user_response = await session.get(current_user_url, headers={"Authorization": f"Bearer {token}"})
        assert current_user_response.status == 200

        current_user_data = UserDataPublic.model_validate(await current_user_response.json())

        assert current_user_data.email == random_user.email
        assert current_user_data.username == random_user.username
