from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.user import User, UserData

class UserRepository(BaseRepository[User, UserData]):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client)