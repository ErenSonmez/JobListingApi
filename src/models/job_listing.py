from beanie import Document

from datetime import datetime
from enum import StrEnum, IntEnum

from models.base import BaseModelFieldData

class Currency(StrEnum):
    US_Dollar = "USD"
    Euro = "EUR"
    UK_Pound = "GBP"

class WorkplaceType(IntEnum):
    OnSite = 1
    Remote = 2
    Hybrid = 3

class ExperienceLevel(IntEnum):
    Entry = 1
    Mid = 2
    Senior = 3
    Executive = 4

class JobListingData(BaseModelFieldData):
    ext_id: str
    title: str
    company: str # TODO: Another document ?
    source_url: str

    date_posted: datetime # when was this job listing posted on source
    date_created: datetime # when was this job listing added to system

    salary_currency: Currency
    min_salary_monthly: int
    max_salary_monthly: int

    location: str # TODO: Placeholder, expand with country/state/city and coordinates maybe ?
    workplace_type: WorkplaceType

    expected_experience: ExperienceLevel
    min_experience_years: int
    max_experience_years: int

    expected_skills: list[str] # TODO: Another document ?

    description: str

class JobListing(JobListingData, Document): ...
