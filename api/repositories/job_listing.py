from beanie.odm.operators.find.logical import Or

from motor.motor_asyncio import AsyncIOMotorClient

from repositories.base import BaseRepository

from models.job_listing import JobListing, JobListingData

class JobListingRepository(BaseRepository[JobListing, JobListingData]):
    def __init__(self, client: AsyncIOMotorClient):
        super().__init__(client)