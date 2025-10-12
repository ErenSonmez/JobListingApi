from pydantic import BaseModel

class LoginRequest(BaseModel):
    usernameOrEmail: str
    password: str