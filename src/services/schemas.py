from pydantic import BaseModel

from beanie import PydanticObjectId

from datetime import datetime

class Token(BaseModel):
    token: str
    expires_at: datetime

class TokenData(BaseModel):
    user_id: PydanticObjectId
    username: str
    email: str