from apps.auth.requests import CreateUserRequest

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from fastapi import APIRouter

router = APIRouter()

@router.get("/user/all")
async def get_all_users():
    repo = await RepositoryFactory.get_repository(UserRepository)
    result = await repo.get_all()
    return result

@router.post("/user/create")
async def create_user(request: CreateUserRequest):
    repo = await RepositoryFactory.get_repository(UserRepository)
    return await repo.create(request.username, request.password, request.email)

