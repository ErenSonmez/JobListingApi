from repositories.schemas import OrderByField
from repositories.job_listing import JobListingRepository

from models.job_listing import JobListing, JobListingData

from services.document import DocumentService

class JobListingService(DocumentService[JobListingRepository, JobListing, JobListingData]):
    default_sort_column = [
        OrderByField(field_name="date_created", ascending=False)
    ]
