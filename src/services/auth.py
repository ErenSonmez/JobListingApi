import os

from typing import Annotated
from beanie import PydanticObjectId

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash

from apps.auth.requests import LoginRequest
from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserDataFull

class AuthService:
    OAUTH2_SCHEME = oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    ENV_SECRET_KEY = "AUTH_SECRET"
    _SECRET = os.getenv(ENV_SECRET_KEY)

    ENV_HASH_SALT_KEY = "AUTH_HASH_SALT"
    _HASH_SALT = os.getenv(ENV_HASH_SALT_KEY)
    _PASSWORD_HASH_ALGORITHM = "HS256"
    _HASHER = PasswordHash.recommended()

    @classmethod
    def _get_secret(cls):
        if cls._SECRET is None:
            cls._SECRET = os.getenv(cls.ENV_SECRET_KEY)

        # TODO: Raise error if secret is none here
        return cls._SECRET

    @classmethod
    def _get_hash_salt(cls):
        if cls._HASH_SALT is None:
            cls._HASH_SALT = os.getenv(cls.ENV_HASH_SALT_KEY)

        return cls._HASH_SALT.encode() if cls._HASH_SALT is not None else None

    @classmethod
    def _hash_password(cls, password: str):
        return cls._HASHER.hash(password, salt=cls._get_hash_salt())

    @classmethod
    def hash_user_password(cls, user: UserDataFull | dict):
        if isinstance(user, UserDataFull):
            user.password = cls._hash_password(user.password)
        else:
            user["password"] = cls._hash_password(user["password"])

        return user

    @classmethod
    async def get_user_by_id(cls, _id: PydanticObjectId):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_by_id(_id)

    @classmethod
    async def create_user(cls, data: UserDataFull | dict):
        data = cls.hash_user_password(data)
        repo = await RepositoryFactory.get_repository(UserRepository)

        return await repo.create(data)

    @classmethod
    async def update_user(cls, _id: PydanticObjectId, data: UserDataFull | dict):
        data = cls.hash_user_password(data)
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.update(data, _id)

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
    async def create_token(cls, user: User):
        # TODO: Not implemented
        return f"{user.id}|{user.username}|{user.password}|{user.email}"

    @classmethod
    async def decode_token(cls, token: str):
        # TODO: Not implemented
        return User(*(token.split("|")))

    @classmethod
    async def get_user_from_token(cls, token: Annotated[str, Depends(OAUTH2_SCHEME)]):
        # TODO: Not implemented, returns first user in db
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_all().first_or_none()