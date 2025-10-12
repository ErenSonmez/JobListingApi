from apps.auth.user.requests import *

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from services.auth import AuthService

from beanie import PydanticObjectId

from fastapi import APIRouter

router = APIRouter()

@router.get("/by_id/{_id}")
async def get_user_by_id(_id: PydanticObjectId):
    return await AuthService.get_user_by_id(_id)

@router.get("/all")
async def get_all_users():
    repo = await RepositoryFactory.get_repository(UserRepository)
    return await repo.get_all().to_list()

@router.post("/")
async def create_user(request: CreateUserRequest):
    # TODO: dont return password hash and id, create response class and map user to it.
    return await AuthService.create_user(request)

@router.put("/{_id}")
async def update_user(_id: PydanticObjectId, request: UpdateUserRequest):
    return await AuthService.update_user(_id, request)