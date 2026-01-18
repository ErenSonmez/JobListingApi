from typing import Any, Optional, Type
from pydantic import BaseModel, FilePath

from beanie import PydanticObjectId

from datetime import datetime

from repositories.base import TRepo

from models.base import TModel, TModelData

import os

# Auth
class Token(BaseModel):
    token: str
    expires_at: datetime

class TokenData(BaseModel):
    user_id: PydanticObjectId
    username: str
    email: str

# Import
ENV_IMPORT_DEFAULT_BATCH_SIZE: int = int(os.getenv("IMPORT_DEFAULT_BATCH_SIZE"))
class ImportJob(BaseModel):
    id: str
    file_path: FilePath
    file_content_type: Optional[str]
    file_extension: Optional[str]
    reader_kwargs: dict[str, Any]

    batch_size: int = ENV_IMPORT_DEFAULT_BATCH_SIZE

    repo_type: Type[TRepo]
    model_type: Type[TModel]
    model_data_type: Type[TModelData]