from apps.auth.requests import *

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from services.auth import AuthService

from beanie import PydanticObjectId

from fastapi import APIRouter

router = APIRouter()

@router.get("/user/{_id}")
async def get_user_by_id(_id: PydanticObjectId):
    return await AuthService.get_user_by_id(_id)

@router.get("/user/all")
async def get_all_users():
    repo = await RepositoryFactory.get_repository(UserRepository)
    return repo.get_all()

@router.post("/user")
async def create_user(request: CreateUserRequest):
    return await AuthService.create_user(request)

@router.put("/user/{_id}")
async def update_user(_id: PydanticObjectId, request: UpdateUserRequest):
    return await AuthService.update_user(_id, request)