from beanie import Document
from motor.motor_asyncio import AsyncIOMotorClient

from functools import wraps

from typing import Any, Awaitable, overload, Type, TypeVar, Generic, Callable, Union

TModel = TypeVar("TModel", bound = Document)

class BaseRepository(Generic[TModel]):
    def __init__(self, client: AsyncIOMotorClient, model: Type[TModel]):
        self._client: AsyncIOMotorClient = client

        self.model = model

    @staticmethod
    def _ensure_model_instance(method: Callable[
            ["BaseRepository[TModel]", TModel | dict[str, Any]]
            , Awaitable[TModel]
            ]) -> Callable[
            ["BaseRepository[TModel]", TModel | dict[str, Any]]
            , Awaitable[TModel]]:
        @wraps(method)
        async def wrapper(self: "BaseRepository[TModel]", item: TModel | dict[str, Any], *args, **kwargs) -> TModel:
            if isinstance(item, dict):
                item = self.model(**item)

            return await method(self, item, *args, **kwargs)

        return wrapper

    async def get_all(self) -> list[TModel]:
        result: list[TModel] = await self.model.all().to_list()
        return result

    @overload
    async def create(self, item: dict[str, Any]) -> TModel: ...

    @overload
    async def create(self, item: TModel) -> TModel: ...

    @_ensure_model_instance
    async def create(self, item: TModel | dict[str, Any]) -> TModel:
        result: TModel = await item.create()
        return result

    @overload
    async def update(self, item: dict[str, Any]) -> TModel: ...

    @overload
    async def update(self, item: TModel) -> TModel: ...

    @_ensure_model_instance
    async def update(self, item: TModel | dict[str, Any]) -> TModel:
        result: TModel = await item.save()
        return result
