from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client, User)