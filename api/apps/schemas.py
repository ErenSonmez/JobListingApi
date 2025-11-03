from pydantic import BaseModel

from typing import TypeVar, Generic

TPageItem = TypeVar("TPageItem", bound = BaseModel)

class BaseRequest(BaseModel): ...
class BaseResponse(BaseModel): ...

class PaginatedResponse(BaseResponse, Generic[TPageItem]):
    page: int
    size: int
    element_count: int
    items: list[TPageItem]