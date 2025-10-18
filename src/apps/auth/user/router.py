from typing import Annotated
from apps.auth.user.requests import *

from repositories.factory import RepositoryFactory
from repositories.user import UserRepository

from models.user import User, UserDataPublic

from services.auth import AuthService
from services.exceptions import UsernameExistsException, EmailExistsException

from beanie import PydanticObjectId

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.get("/me")
async def get_current_user_info(user: Annotated[User, Depends(AuthService.get_user_from_token)]):
    return UserDataPublic.model_validate(user.model_dump())

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
    try:
        new_user = await AuthService.create_user(request)
    except UsernameExistsException:
        raise HTTPException(status_code=400, detail=f"Username '{request.username}' is taken")
    except EmailExistsException:
        raise HTTPException(status_code=400, detail=f"Email '{request.email}' is used by another user")

    return new_user

@router.put("/{_id}")
async def update_user(_id: PydanticObjectId, request: UpdateUserRequest):
    return await AuthService.update_user(_id, request)