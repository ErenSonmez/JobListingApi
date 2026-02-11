import os
from typing import Any, Generic, Mapping, get_args, get_origin

from beanie import Document, PydanticObjectId

from services.base import BaseService
from services.exceptions import BadEnvironmentValueException, DocumentNotFoundByIdException, MissingEnvironmentVariableException

from apps.schemas import PaginatedResponse

from models.base import TModel, TModelData

from repositories.base import BaseRepository, TRepo
from repositories.factory import RepositoryFactory
from repositories.schemas import OrderByField

class DocumentService(BaseService, Generic[TRepo, TModel, TModelData]):
    ENV_MAX_PER_PAGE_KEY = "MAX_PER_PAGE"
    MAX_PER_PAGE: int = None

    default_order_by: list[OrderByField] = []
    def __init_subclass__(self):
        super().__init_subclass__()

        self._repo = None
        self._model_type = None
        for base in self.__orig_bases__: # get generic types
            if get_origin(base) is DocumentService:
                args_ = get_args(base)
                for arg_ in args_:
                    if issubclass(arg_, BaseRepository):
                        self._repo_type = arg_
                    if issubclass(arg_, Document):
                        self._model_type = arg_

    async def _get_repo(self):
        if self._repo is None:
            self._repo: BaseRepository[TModel, TModelData] = await RepositoryFactory.get_repository(self._repo_type)
        
        return self._repo

    async def get_by_id(self, _id: PydanticObjectId):
        item = await self._repo.get_by_id(_id)
        if item is None:
            raise DocumentNotFoundByIdException(self._model_type, _id)

        return item

    @property
    def max_per_page(self):
        if self.MAX_PER_PAGE is None:
            val = os.getenv(self.ENV_MAX_PER_PAGE_KEY)

            if val is None:
                raise MissingEnvironmentVariableException(self.ENV_MAX_PER_PAGE_KEY)

            try:
                self.MAX_PER_PAGE = int(val)
            except ValueError:
                raise BadEnvironmentValueException(f"Environment variable {self.ENV_MAX_PER_PAGE_KEY} must be int-convertible")

        return self.MAX_PER_PAGE

    async def element_count(self, *filter_mappings: tuple[Mapping[Any, Any]]):
        repo = await self._get_repo()

        return await repo.find(*filter_mappings).count()

    async def get_page(self, page: int, size: int, *filter_mappings: tuple[Mapping[Any, Any]], order_by: list[OrderByField] = None):
        repo = await self._get_repo()

        if not order_by:
            order_by = self.default_order_by.copy()

        if page < 1:
            page = 1

        if size <= 0:
            size = 1
        elif size > self.max_per_page:
            size = self.max_per_page

        query = repo.find(*filter_mappings, order_by = order_by)

        element_count = await query.count()
        items = await query.skip((page - 1) * size).limit(size).to_list()

        return PaginatedResponse(
            page = page,
            size = size,
            element_count = element_count,
            items = items
        )