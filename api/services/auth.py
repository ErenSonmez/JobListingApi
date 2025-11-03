import os

from typing import Annotated
from beanie import PydanticObjectId

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

import jwt
import json

from datetime import datetime, timedelta

from apps.auth.requests import LoginRequest
from apps.auth.responses import LoginResponse

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserDataFull

from services.exceptions import BadEnvironmentValueException, EmailExistsException, IncorrectPasswordException, UserNotFoundExcepotion, UsernameExistsException
from services.schemas import Token, TokenData

class PydanticObjectIdEncoder(json.JSONEncoder):
    def default(self, value):
        if isinstance(value, PydanticObjectId):
            return str(value)

        return json.JSONEncoder.default(self, value)

class AuthService:
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="/auth/login")

    ENV_SECRET_KEY = "AUTH_SECRET"
    _SECRET = os.getenv(ENV_SECRET_KEY)

    ENV_ACCESS_TOKEN_VALID_MINUTES_KEY = "AUTH_ACCESS_TOKEN_VALID_MINUTES"
    ENV_ACCESS_TOKEN_VALID_SECONDS_KEY = "AUTH_ACCESS_TOKEN_VALID_SECONDS"
    _ACCESS_TOKEN_VALID_TIMEDELTA = None

    ENV_HASH_SALT_KEY = "AUTH_HASH_SALT"
    _HASH_SALT = os.getenv(ENV_HASH_SALT_KEY)

    _TOKEN_HASH_ALGORITHM = "HS256"

    _PASSWORD_HASHER = PasswordHash.recommended()

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
    def _get_access_token_valid_timedelta_from_env(cls):
        valid_seconds = os.getenv(cls.ENV_ACCESS_TOKEN_VALID_SECONDS_KEY)
        if valid_seconds and valid_seconds.isdigit():
            valid_timedelta = timedelta(seconds=int(valid_seconds))
            return valid_timedelta

        valid_minutes = os.getenv(cls.ENV_ACCESS_TOKEN_VALID_MINUTES_KEY)
        if valid_minutes and valid_minutes.isdigit():
            valid_timedelta = timedelta(minutes=int(valid_minutes))
            return valid_timedelta

        raise BadEnvironmentValueException(
            f"Missing or bad value for access token expiry date. " +
            f"Keys checked: {cls.ENV_ACCESS_TOKEN_VALID_SECONDS_KEY} - {cls.ENV_ACCESS_TOKEN_VALID_MINUTES_KEY}. " +
            f"Values should be integers. If both provided, {cls.ENV_ACCESS_TOKEN_VALID_SECONDS_KEY} will be used."
        )

    @classmethod
    def _get_access_token_valid_timedelta(cls):
        if cls._ACCESS_TOKEN_VALID_TIMEDELTA is None:
            cls._ACCESS_TOKEN_VALID_TIMEDELTA = cls._get_access_token_valid_timedelta_from_env()

        return cls._ACCESS_TOKEN_VALID_TIMEDELTA


    @classmethod
    def _hash_password(cls, password: str):
        return cls._PASSWORD_HASHER.hash(password, salt=cls._get_hash_salt())

    @classmethod
    def _get_token_data_from_user(cls, user: User):
        return TokenData(
            user_id = user.id,
            username = user.username,
            email = user.email,
        )

    @classmethod
    def verify_password(cls, password: str, hashed_password: str):
        try:
            return cls._PASSWORD_HASHER.verify(password, hashed_password)
        except UnknownHashError:
            return False

    @classmethod
    async def get_user_by_id(cls, _id: PydanticObjectId):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_by_id(_id)

    @classmethod
    async def create_user(cls, data: UserDataFull):
        repo = await RepositoryFactory.get_repository(UserRepository)

        user_by_username = await repo.fetch_by_username(data.username)
        if user_by_username is not None:
            raise UsernameExistsException(data.username)

        user_by_email = await repo.fetch_by_email(data.email)
        if user_by_email is not None:
            raise EmailExistsException(data.email)

        create_data = data.model_copy()
        create_data.password = cls._hash_password(create_data.password)

        return await repo.create(create_data)

    @classmethod
    async def update_user(cls, _id: PydanticObjectId, data: UserDataFull):
        data.password = cls._hash_password(data.password)
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.update(data, _id)

    @classmethod
    def create_token(cls, user: User, valid_timedelta: timedelta = None):
        if valid_timedelta is None:
            valid_timedelta = cls._get_access_token_valid_timedelta()

        token_expires_at = datetime.now() + valid_timedelta

        token_data = cls._get_token_data_from_user(user)
        token_data_dict = token_data.model_dump() | {"exp": token_expires_at}

        token = jwt.encode(
            token_data_dict,
            cls._get_secret(),
            algorithm=cls._TOKEN_HASH_ALGORITHM,
            json_encoder=PydanticObjectIdEncoder
        )

        return Token(
            token = token,
            expires_at = token_expires_at,
        )

    @classmethod
    async def login(cls, request: LoginRequest):
        repo = await RepositoryFactory.get_repository(UserRepository)
        user = await repo.fetch_by_email_or_username(request.usernameOrEmail)
        print("login user", user,"request",request)

        print("email",await repo.fetch_by_email(request.usernameOrEmail))
        print("username",await repo.fetch_by_username(request.usernameOrEmail))

        if user is None:
            raise UserNotFoundExcepotion(request.usernameOrEmail)

        if not cls.verify_password(request.password, user.password):
            raise IncorrectPasswordException(user, request.password)

        token = cls.create_token(user)

        return LoginResponse(
            token = token
        )

    @classmethod
    def decode_token(cls, token: str | Token):
        if isinstance(token, Token):
            token = token.token

        token_data_dict = jwt.decode(
            token,
            cls._get_secret(),
            algorithms=[cls._TOKEN_HASH_ALGORITHM]
        )
        token_data = TokenData.model_validate(token_data_dict)

        return token_data

    @classmethod
    async def get_user_from_token(cls, token: Annotated[str, Depends(OAUTH2_SCHEME)]):
        token_data = cls.decode_token(token)
        repo = await RepositoryFactory.get_repository(UserRepository)
        return await repo.get_by_id(token_data.user_id)