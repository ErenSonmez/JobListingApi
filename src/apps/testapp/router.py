import asyncio

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository
from repositories.schemas import MongoClientCredentials

from models.user import User

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.get("/test-user_create")
async def test_user_create(repo_name: str):
    repo = await RepositoryFactory.get_repository(UserRepository)
    return await repo.create("test","123","test@test.com")

@router.post("/reset-db-credentials")
async def reset_db_credentials(creds: MongoClientCredentials):
    await RepositoryFactory.set_db_credentials(creds)
    return creds