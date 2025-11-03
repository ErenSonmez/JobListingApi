
from typing import Type, TypeVar

from repositories.base import TRepo

from models.base import TModel, TModelData

from models.user import User, UserDataFull
from repositories.user import UserRepository

from models.job_listing import JobListing, JobListingData
from repositories.job_listing import JobListingData, JobListingRepository

from services.base import BaseService

from services.data_import import ImportService
from services.job_listing import JobListingService

_SERVICE_TYPE = TypeVar("_SERVICE_TYPE", bound=BaseService)

class ServiceFactory:
    @classmethod
    def get_service(cls, service_type: Type[_SERVICE_TYPE], *args, **kwargs):
        return service_type(*args, **kwargs)

    @classmethod
    def get_job_listing_service(cls):
        return cls.get_service(JobListingService)

    @classmethod
    def get_import_service(cls):
        return cls.get_service(ImportService)