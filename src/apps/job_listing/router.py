from beanie import PydanticObjectId

from repositories.factory import RepositoryFactory
from repositories.job_listing import JobListingRepository

from models.job_listing import JobListingData

from fastapi import APIRouter, UploadFile

router = APIRouter(tags=["Job listings"])

# TODO: Add response classes

@router.get("/all")
async def get_all_listings():
    # TODO: For debugging, remove later
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.get_all().to_list()

@router.get("/")
async def get_listing_page(page: int = 1, size: int = 10):
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.get_page(page, size).to_list()

@router.get("/by_id/{_id}")
async def get_listing_by_id(_id: PydanticObjectId):
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.get_by_id(_id)

@router.post("/")
async def create_job_listing(request: JobListingData):
    listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    return await listing_repo.create(request)

@router.post("/upload")
async def upload_listings(file: UploadFile):
    # TODO: Create service
    return ""

