from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.user import User

class UserRepository(BaseRepository):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client)

    def create(self, username: str, password: str):
        user = User(username=username, password=password)
        return user.create()

    def get_all(self):
        return User.all().to_list()