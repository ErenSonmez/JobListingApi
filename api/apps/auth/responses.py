from apps.schemas import BaseResponse
from services.schemas import Token

class LoginResponse(BaseResponse):
    token: Token