from apps.auth.requests import LoginRequest

from apps.auth.responses import LoginResponse
from services.auth import AuthService

from fastapi import APIRouter, HTTPException

from services.exceptions import UserNotFoundExcepotion

router = APIRouter()

@router.post("/login")
async def login(request: LoginRequest):
    try:
        token = await AuthService.login(request)
    except UserNotFoundExcepotion:
        raise HTTPException(status_code=400, detail="Incorrect username/email or password")

    return LoginResponse.model_validate(token.model_dump())

from apps.auth.user.router import router as user_router
router.include_router(user_router, prefix="/user")