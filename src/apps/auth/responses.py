from pydantic import BaseModel
from services.schemas import Token

class LoginResponse(BaseModel):
    token: Token