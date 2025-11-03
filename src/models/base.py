from beanie import Document
from typing import TypeVar
from pydantic import BaseModel

class BaseModelFieldData(BaseModel): ...

TModel = TypeVar("TModel", bound = Document)
TModelData = TypeVar("TModelData", bound = BaseModelFieldData)