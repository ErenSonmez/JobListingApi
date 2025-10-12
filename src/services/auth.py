from typing import Annotated
from beanie import PydanticObjectId

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from apps.auth.requests import LoginRequest
from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserDataFull

class AuthService:
    OAUTH2_SCHEME = oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    @classmethod
    async def get_user_by_id(cls, _id: PydanticObjectId):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_by_id(_id)

    @classmethod
    async def create_user(cls, data: UserDataFull | dict):
        # TODO: Add password hashing
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.create(data)

    @classmethod
    async def update_user(cls, _id: PydanticObjectId, data: UserDataFull | dict):
        # TODO: Add password hashing
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.update(data, _id)

    @classmethod
    async def create_token(cls, user: User):
        # TODO: Not implemented
        return f"{user.id}-{user.username}-{user.email}"

    @classmethod
    async def login(cls, request: LoginRequest):
        repo = await RepositoryFactory.get_repository(UserRepository)
        user = await repo.find(
            (User.username == request.usernameOrEmail or User.email == request.usernameOrEmail) and
            User.password == request.password # TODO: Add password hashing
        ).first_or_none()

        if user is None:
            return None

        return await cls.create_token(user)

    @classmethod
    async def decode_token(cls, token: str):
        # TODO: Not implemented
        pass

    @classmethod
    async def get_user_from_token(cls, token: Annotated[str, Depends(OAUTH2_SCHEME)]):
        # TODO: Not implemented, returns first user in db
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_all().first_or_none()