import asyncio

from models.user import User
from repositories.factory import RepositoryFactory
from repositories.schemas import MongoClientCredentials

from services.auth import AuthService

from fastapi import APIRouter, Depends

from typing import Annotated

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.post("/reset-db-credentials")
async def reset_db_credentials(creds: MongoClientCredentials):
    await RepositoryFactory.set_db_credentials(creds)
    return creds

@router.get("/auth-test")
async def auth_test(user: Annotated[User, Depends(AuthService.get_user_from_token)]):
    return {"user": user}

