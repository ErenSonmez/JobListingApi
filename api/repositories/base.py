from beanie import Document, PydanticObjectId, SortDirection
from beanie.odm.queries.find import FindOne, FindMany
from beanie.odm.queries.delete import DeleteOne

from motor.motor_asyncio import AsyncIOMotorClient

from typing import Any, Awaitable, Iterable, Mapping, get_origin, overload, TypeVar, Generic, Callable, get_args, Self

from pydantic import ValidationError

from repositories.exceptions import MissingIdException, ModelValidationException, OrderFieldNotExistsException

from models.base import BaseModelFieldData, TModel, TModelData
from repositories.schemas import OrderByField

# TODO: Write query tests

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
                        self._model_type = arg_
                    elif issubclass(arg_, BaseModelFieldData):
                        self._model_data_type = arg_

    def _ensure_model_instance(self, item: TModel | TModelData | dict[str, Any]) -> TModel:
        try:
            if isinstance(item, self._model_type):
                return item

            if isinstance(item, dict):
                return self._model_type.model_validate(item)

            if isinstance(item, self._model_data_type):
                item_data: TModelData = item
                return self._model_type.model_validate(item_data.model_dump())
        except ValidationError as ex:
            raise ModelValidationException(item, self._model_type, ex.errors())

        raise ModelValidationException(item, self._model_type)

    def _ensure_model_iterable(self, items: Iterable[TModel | TModelData | dict[str, Any]]) -> Iterable[TModel]:
        return [self._ensure_model_instance(item) for item in items]

    def _parse_order_by(self, order_by: list[OrderByField]):
        parsed_order_by = []

        model_fields = set(self._model_type.model_fields.keys())
        for order_by_field in order_by:
            field_name = order_by_field.field_name
            if field_name not in model_fields:
                raise OrderFieldNotExistsException(field_name, self._model_type)

            direction = SortDirection.ASCENDING if order_by_field.ascending else SortDirection.DESCENDING
            parsed_order_by.append((field_name, direction))

        return parsed_order_by

    # Read
    def find(self, *query: Mapping[Any, Any] | bool, order_by: list[OrderByField] = None) -> FindMany[TModel]:
        result = self._model_type.find(*query)
        if order_by is not None:
            parsed_order_by = self._parse_order_by(order_by)
            result.sort(parsed_order_by)

        return result

    def get_by_id(self, _id: PydanticObjectId) -> FindOne[TModel]:
        return self._model_type.find_one({"_id": _id})

    def get_all(self) -> FindMany[TModel]:
        return self._model_type.all()

    # Create
    @overload
    def create(self, item: dict[str, Any]) -> Awaitable[TModel]: ...

    @overload
    def create(self, item: TModel) -> Awaitable[TModel]: ...

    @overload
    def create(self, item: TModelData) -> Awaitable[TModel]: ...

    def create(self, item: TModel | TModelData | dict[str, Any]) -> Awaitable[TModel]:
        return self._ensure_model_instance(item).create()

    def create_many(self, items: Iterable[TModel | TModelData | dict[str, Any]]):
        items = self._ensure_model_iterable(items)
        return self._model_type.insert_many(items)

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

    def update(self, item: TModel, _id: PydanticObjectId | None = None) -> Awaitable[TModel]:
        item = self._ensure_model_instance(item)
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

        elif isinstance(item_data, self._model_type) and item_data.id is not None:
            _id = item_data.id

        else:
            raise MissingIdException("ID is required either in data object or as parameter for delete.")

        return self.get_by_id(_id).delete()

TRepo = TypeVar("TRepo", bound=BaseRepository)