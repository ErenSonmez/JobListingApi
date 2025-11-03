from beanie import PydanticObjectId

from apps.schemas import PaginatedResponse
from repositories.factory import RepositoryFactory
from repositories.job_listing import JobListingRepository

from models.job_listing import JobListing, JobListingData

from fastapi import APIRouter, Depends, UploadFile

from services.data_import import ImportService
from services.factory import ServiceFactory
from services.job_listing import JobListingService

router = APIRouter(tags=["Job listings"])

# TODO: Add response classes

@router.get("/all")
async def get_all_listings():
    # TODO: For debugging, remove later
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.get_all().to_list()

@router.get("/")
async def get_listing_page(page: int = 1, size: int = 10, listing_service: JobListingService = Depends(ServiceFactory.get_job_listing_service)):
    return await listing_service.get_page(page, size)

@router.get("/by_id/{_id}")
async def get_listing_by_id(_id: PydanticObjectId):
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.get_by_id(_id)

@router.post("/")
async def create_job_listing(request: JobListingData):
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.create(request)

@router.post("/upload")
async def upload_listings(file: UploadFile, import_service: ImportService = Depends(ServiceFactory.get_import_service)):
    job = await import_service.import_file(file, JobListing, JobListingData, JobListingRepository)
    return {
        "job": job.id,
        "filename":file.filename,
        "content_type":file.content_type,
        "headers":file.headers,
        "size":file.size,
    }

