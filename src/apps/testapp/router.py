import asyncio

from repositories.base import BaseRepository

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.get("/test-repo")
async def test_repo():
    repo = BaseRepository()
    return repo._client.list_database_names()