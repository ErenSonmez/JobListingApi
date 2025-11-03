from beanie.odm.operators.find.logical import Or

from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.user import User, UserDataFull

class UserRepository(BaseRepository[User, UserDataFull]):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client)

    def fetch_by_email_or_username(self, usernameOrEmail: str):
        return self.find(
            Or(User.username == usernameOrEmail, User.email == usernameOrEmail)
        ).first_or_none()

    def fetch_by_username(self, username: str):
        return self.find(User.username == username).first_or_none()

    def fetch_by_email(self, email: str):
        return self.find(User.email == email).first_or_none()