# import pymongo
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

class BaseRepository:
    def __init__(self, client: AsyncIOMotorClient):
        self._client: AsyncIOMotorClient = client