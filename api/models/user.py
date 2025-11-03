from beanie import Document
from pydantic import EmailStr

from models.base import BaseModelFieldData

class UserDataPublic(BaseModelFieldData):
    # does not include sensitive data
    username: str
    email: EmailStr

class UserDataFull(UserDataPublic):
    password: str

class User(UserDataFull, Document): ...
