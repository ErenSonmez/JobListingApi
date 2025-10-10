from apps.auth.requests import *

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from beanie import PydanticObjectId

from fastapi import APIRouter

router = APIRouter()

@router.get("/user/all")
async def get_all_users():
    repo = await RepositoryFactory.get_repository(UserRepository)
    result = await repo.get_all()
    return result

@router.post("/user")
async def create_user(request: CreateUserRequest):
    repo = await RepositoryFactory.get_repository(UserRepository)
    new_user = await repo.create(request.model_dump())
    return new_user

@router.put("/user/{_id}")
async def update_user(_id: PydanticObjectId, request: UpdateUserRequest):
    repo = await RepositoryFactory.get_repository(UserRepository)
    updated_user = await repo.update(request.model_dump() | {"_id": _id})
    return updated_user