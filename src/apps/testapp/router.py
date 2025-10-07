import asyncio

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.get("/test-user_create")
async def test_user_create(repo_name: str):
    repo = RepositoryFactory.get_repository(UserRepository)
    return await repo.create("test","123")

@router.get("/test-user_get_all")
async def test_user_get_all(repo_name: str):
    repo = RepositoryFactory.get_repository(UserRepository)
    result = await repo.get_all()
    return result