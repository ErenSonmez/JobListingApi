from typing import Generic, get_args, get_origin

from services.base import BaseService

from apps.schemas import PaginatedResponse

from models.base import TModel, TModelData

from repositories.base import BaseRepository, TRepo
from repositories.factory import RepositoryFactory

# TODO: Write tests

class DocumentService(BaseService, Generic[TRepo, TModel, TModelData]):
    def __init_subclass__(self):
        super().__init_subclass__()

        self._repo = None
        for base in self.__orig_bases__: # get generic types
            if get_origin(base) is DocumentService:
                args_ = get_args(base)
                for arg_ in args_:
                    if issubclass(arg_, BaseRepository):
                        self._repo_type = arg_

    async def _get_repo(self):
        if self._repo is None:
            self._repo: BaseRepository[TModel, TModelData] = await RepositoryFactory.get_repository(self._repo_type)
        
        return self._repo

    async def get_page(self, page: int, size: int):
        repo = await self._get_repo()

        return PaginatedResponse(
            page = page,
            size = size,
            element_count = await repo.element_count(),
            items = await repo.get_page(page, size).to_list()
        )