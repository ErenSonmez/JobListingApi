from typing import overload
from beanie import PydanticObjectId
from models.listing_shortlist import ShortlistedListing
from models.user import User
from repositories.schemas import OrderByField
from repositories.job_listing import JobListingRepository

from models.job_listing import JobListing, JobListingData

from services.document import DocumentService

class JobListingService(DocumentService[JobListingRepository, JobListing, JobListingData]):
    default_sort_column = [
        OrderByField(field_name="date_created", ascending=False)
    ]

    @overload
    async def shortlist_listing(self, user: User, listing: JobListing): ...

    @overload
    async def shortlist_listing(self, user: User, listing: PydanticObjectId): ...

    async def shortlist_listing(self, user: User, listing: JobListing | PydanticObjectId):
        if isinstance(listing, PydanticObjectId):
            listing = self.get_by_id(listing)

        shortlist_item = ShortlistedListing(user = user, listing = listing)
        await shortlist_item.create()

        return shortlist_item()
