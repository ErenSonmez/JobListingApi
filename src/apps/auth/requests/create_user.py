from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
