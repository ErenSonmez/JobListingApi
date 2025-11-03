from apps.schemas import BaseRequest

class LoginRequest(BaseRequest):
    usernameOrEmail: str
    password: str