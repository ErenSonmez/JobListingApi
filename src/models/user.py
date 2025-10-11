from beanie import Document
from pydantic import EmailStr, BaseModel

from models.base import BaseModelFieldData

class UserData(BaseModelFieldData):
    username: str
    password: str
    email: EmailStr

class User(UserData, Document): ...
