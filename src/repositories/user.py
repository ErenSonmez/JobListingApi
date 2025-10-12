from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.user import User, UserDataFull

class UserRepository(BaseRepository[User, UserDataFull]):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client)