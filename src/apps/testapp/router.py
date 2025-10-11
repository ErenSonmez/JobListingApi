import asyncio

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository
from repositories.schemas import MongoClientCredentials

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.post("/reset-db-credentials")
async def reset_db_credentials(creds: MongoClientCredentials):
    await RepositoryFactory.set_db_credentials(creds)
    return creds