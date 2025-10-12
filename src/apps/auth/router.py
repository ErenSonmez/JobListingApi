from typing import Annotated

from apps.auth.requests import LoginRequest

from services.auth import AuthService

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], response: Response):
    request = LoginRequest(
        usernameOrEmail = form_data.username,
        password = form_data.password
    )
    token = await AuthService.login(request)
    if token is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"detail": "User not found"}

    return {"token": token}



from apps.auth.user.router import router as user_router
router.include_router(user_router, prefix="/user")