from repositories.factory import RepositoryFactory

from repositories.user import UserRepository

class AuthService:
    async def create_user(self):
        repo = await RepositoryFactory.get_repository(UserRepository)
