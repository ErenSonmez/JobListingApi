from beanie import Document, PydanticObjectId
from beanie.odm.queries.find import FindOne, FindMany
from beanie.odm.queries.delete import DeleteOne

from motor.motor_asyncio import AsyncIOMotorClient

from functools import wraps

from typing import Any, Awaitable, List, Mapping, get_origin, overload, TypeVar, Generic, Callable, get_args
from pydantic import BaseModel, ValidationError

from repositories.exceptions import MissingIdException

from models.base import BaseModelFieldData

TModel = TypeVar("TModel", bound = Document)
TModelData = TypeVar("TModelData", bound = BaseModelFieldData)

class BaseRepository(Generic[TModel, TModelData]):
    def __init__(self, client: AsyncIOMotorClient):
        self._client: AsyncIOMotorClient = client

    def __init_subclass__(self):
        super().__init_subclass__()

        for base in self.__orig_bases__: # get generic types
            if get_origin(base) is BaseRepository:
                args_ = get_args(base)
                for arg_ in args_:
                    if issubclass(arg_, Document):
                        self._model = arg_
                    elif issubclass(arg_, BaseModelFieldData):
                        self._model_data = arg_

    @staticmethod
    def _ensure_model_instance(method: Callable[
                ["BaseRepository[TModel]"],
                Callable[["BaseRepository[TModel]"], Awaitable[TModel]]
            ]) -> Callable[
                ["BaseRepository[TModel]"],
                Callable[["BaseRepository[TModel]"], Awaitable[TModel]]
            ]:
        @wraps(method)
        def wrapper(self: "BaseRepository[TModel]", *args, **kwargs) -> TModel:
            new_args=[]
            for arg_ in args:
                if isinstance(arg_, dict):
                    try:
                        arg_ = self._model.model_validate(arg_)
                    except ValidationError:
                        pass

                elif isinstance(arg_, self._model_data):
                    try:
                        item_data: TModelData = arg_
                        arg_ = self._model.model_validate(item_data.model_dump())
                    except ValidationError:
                        pass

                new_args.append(arg_)

            return method(self, *new_args, **kwargs)

        return wrapper

    # Read
    def find(self, query: Mapping[Any, Any] | bool) -> FindMany[TModel]:
        return self._model.find(query)

    def get_by_id(self, _id: PydanticObjectId) -> FindOne[TModel]:
        return self._model.find_one({"_id": _id})

    def get_all(self) -> FindMany[TModel]:
        return self._model.all()

    # Create
    @overload
    def create(self, item: dict[str, Any]) -> Awaitable[TModel]: ...

    @overload
    def create(self, item: TModel) -> Awaitable[TModel]: ...

    @overload
    def create(self, item: TModelData) -> Awaitable[TModel]: ...

    @_ensure_model_instance
    def create(self, item: TModel | TModelData | dict[str, Any]) -> Awaitable[TModel]:
        return item.create()

    # Update
    @overload
    def update(self, item: dict[str, Any], _id: PydanticObjectId) -> Awaitable[TModel]: ...

    @overload
    def update(self, item: dict[str, Any]) -> Awaitable[TModel]: ...

    @overload
    def update(self, item: TModel, _id: PydanticObjectId) -> Awaitable[TModel]: ...

    @overload
    def update(self, item: TModel) -> Awaitable[TModel]: ...

    @overload
    def update(self, item_data: TModelData, _id: PydanticObjectId) -> Awaitable[TModel]: ...

    @_ensure_model_instance
    def update(self, item: TModel, _id: PydanticObjectId | None = None) -> Awaitable[TModel]:
        if _id is None:
            if item.id is None:
                raise MissingIdException("ID is required either in data object or as parameter for update.")
        else: # if id is sent as parameter set it regardless if id is present in item or not
            item.id = _id


        return item.save()

    # Delete
    @overload
    def delete(self, item: TModel) -> DeleteOne: ...

    @overload
    def delete(self, _id: PydanticObjectId) -> DeleteOne: ...

    def delete(self, item_data: PydanticObjectId | TModel) -> DeleteOne:
        if isinstance(item_data, PydanticObjectId):
            _id = item_data

        elif isinstance(item_data, self._model) and item_data.id is not None:
            _id = item_data.id

        else:
            raise MissingIdException("ID is required either in data object or as parameter for delete.")

        return self.get_by_id(_id).delete()

    def get_page(self, page: int, size: int) -> FindMany[TModel]:
        # TODO: Add filtering
        if page < 1:
            page = 1

        if size > 100:
            size = 100

        return (self._model
                        .all()
                        .skip((page - 1) * size)
                        .limit(size)
                )