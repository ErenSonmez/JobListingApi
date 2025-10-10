from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

class UpdateUserRequest(BaseModel):
    # id: PydanticObjectId
    username: str
    password: str
    email: EmailStr