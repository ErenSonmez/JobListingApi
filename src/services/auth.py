from beanie import PydanticObjectId
from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import UserData

class AuthService:
    @classmethod
    async def get_user_by_id(cls, _id: PydanticObjectId):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return repo.get_by_id(_id)

    @classmethod
    async def create_user(cls, data: UserData | dict):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return repo.create(data)

    @classmethod
    async def update_user(cls, _id: PydanticObjectId, data: UserData | dict):
        repo = await RepositoryFactory.get_repository(UserRepository)
        return repo.update(data, _id)