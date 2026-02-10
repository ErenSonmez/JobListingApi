import pytest_asyncio

import logging
import uuid

from datetime import datetime

from beanie import PydanticObjectId

from models.job_listing import Currency, JobListing, JobListingData, WorkplaceType

from repositories.factory import RepositoryFactory
from repositories.job_listing import JobListingRepository
from repositories.user import UserRepository

from models.user import User, UserDataFull

def generate_random_user_data(username: str = None, password: str = None, email: str = None,
                              username_prefix: str = "", email_prefix: str = ""):
    if not username:
        username = uuid.uuid4().hex

    if not password:
        password = uuid.uuid4().hex

    if not email:
        email = f"{username}@testmail.com"

    if username_prefix:
        username = f"{username_prefix}{username}"

    if email_prefix:
        email = f"{email_prefix}{email}"

    return UserDataFull(
        username = username,
        password = password,
        email = email,
    )

@pytest_asyncio.fixture(scope="session")
async def setup_teardown_users():
    logging.info("setup_teardown_users setup start")
    users_to_delete: list[User] = []
    user_ids_to_delete: list[PydanticObjectId] = []

    logging.info("setup_teardown_users setup end")
    yield users_to_delete, user_ids_to_delete

    logging.info("setup_teardown_users teardown start")
    user_repo = await RepositoryFactory.get_repository(UserRepository)
    for user in users_to_delete:
        if user is not None:
            logging.info(f"setup_teardown_users teardown deleting user {user}")
            await user_repo.delete(user)

    for user_id in user_ids_to_delete:
        if user_id is not None:
            logging.info(f"setup_teardown_users teardown deleting user with id {user_id}")
            await user_repo.delete(user_id)
    logging.info("setup_teardown_users teardown end")

def generate_random_listing(
        ext_id = None,
        title = None,
        company = None,
        source_url = None,
        date_posted = None,
        date_created = None,
        salary_currency = None,
        min_salary_monthly = None,
        max_salary_monthly = None,
        location = None,
        workplace_type = None,
        expected_experience = None,
        min_experience_years = None,
        max_experience_years = None,
        expected_skills = None,
        description = None,
        ext_id_prefix: str = None, title_prefix: str = None):

    item = JobListingData(
        ext_id = ext_id if ext_id is not None else uuid.uuid4().hex,
        title = title if title is not None else uuid.uuid4().hex,
        company = company if company is not None else uuid.uuid4().hex,
        source_url = source_url if source_url is not None else uuid.uuid4().hex,
        date_posted = date_posted if date_posted is not None else datetime.now(),
        date_created = date_created if date_created is not None else datetime.now(),
        salary_currency = salary_currency if salary_currency is not None else Currency.US_Dollar,
        min_salary_monthly = min_salary_monthly,
        max_salary_monthly = max_salary_monthly,
        location = location if location is not None else uuid.uuid4().hex,
        workplace_type = workplace_type if workplace_type is not None else WorkplaceType.OnSite,
        expected_experience = expected_experience,
        min_experience_years = min_experience_years,
        max_experience_years = max_experience_years,
        expected_skills = expected_skills if expected_skills is not None else [uuid.uuid4().hex],
        description = description if description is not None else uuid.uuid4().hex
    )
    if ext_id_prefix is not None:
        item.ext_id = f"{ext_id_prefix}{item.ext_id}"

    if title_prefix is not None:
        item.title = f"{title_prefix}{item.title}"

    print(item.title, item.ext_id)
    return item

@pytest_asyncio.fixture(scope="session")
async def setup_teardown_job_listings():
    logging.info("setup_teardown_job_listings setup start")
    job_listings_to_delete: list[JobListing] = []
    job_listing_ids_to_delete: list[PydanticObjectId] = []

    logging.info("setup_teardown_job_listings setup end")
    yield job_listings_to_delete, job_listing_ids_to_delete

    logging.info("setup_teardown_job_listings teardown start")
    job_listing_repo = await RepositoryFactory.get_repository(JobListingRepository)
    for job_listing in job_listings_to_delete:
        if job_listing is not None:
            logging.info(f"setup_teardown_job_listings teardown deleting job_listing {job_listing}")
            await job_listing_repo.delete(job_listing)

    for job_listing_id in job_listing_ids_to_delete:
        if job_listing_id is not None:
            logging.info(f"setup_teardown_job_listings teardown deleting job_listing with id {job_listing_id}")
            await job_listing_repo.delete(job_listing_id)
    logging.info("setup_teardown_job_listings teardown end")