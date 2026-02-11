from beanie import Document, Link

from models.base import BaseModelFieldData
from models.job_listing import JobListing
from models.user import User

class ShortlistedListingData(BaseModelFieldData):
    user: Link[User]
    listing: Link[JobListing]

class ShortlistedListing(ShortlistedListingData, Document): ...