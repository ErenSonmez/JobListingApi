import pytest

import logging

from beanie.odm.operators.find.evaluation import Text

from apps.schemas import PaginatedResponse

from repositories.base import BaseRepository
from services.document import DocumentService
from services.factory import ServiceFactory
from services.job_listing import JobListingService


pytest_plugins = ('pytest_asyncio',)

document_services = [
    ServiceFactory.get_job_listing_service()
]

document_service_filter_examples = {
    JobListingService: [
        Text('"developer" -"Full Stack"', case_sensitive=False),
    ]
}

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'document_service',
    document_services,
    ids = lambda cls: cls.__class__.__name__,
)
async def test_get_repo(document_service: DocumentService):
    repo = await document_service._get_repo()

    assert isinstance(repo, BaseRepository)
    assert isinstance(repo, document_service._repo_type)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'document_service',
    document_services,
    ids = lambda cls: cls.__class__.__name__,
)
async def test_get_element_count(document_service: DocumentService):
    repo = await document_service._get_repo()

    service_element_count = await document_service.element_count()
    repo_element_count = await repo.get_all().count()
    assert service_element_count == repo_element_count

    filter_example = document_service_filter_examples.get(type(document_service), [])
    filtered_service_element_count = await document_service.element_count(*filter_example)
    filtered_repo_element_count = await repo.find(*filter_example).count()
    assert filtered_service_element_count == filtered_repo_element_count

@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    'document_service',
    document_services,
    ids = lambda cls: cls.__class__.__name__,
)
async def test_get_page(document_service: DocumentService):
    element_count = await document_service.element_count()
    max_per_page = document_service.max_per_page
    if element_count <= document_service.max_per_page:
        logging.warning(f"cannot run test_get_page with service {document_service.__class__.__name__} - {element_count=} - must have more than {max_per_page=}")

    # Default case
    p1_s10 = await document_service.get_page(1, 10)

    assert isinstance(p1_s10, PaginatedResponse)
    assert p1_s10.element_count == element_count
    assert p1_s10.page == 1
    assert p1_s10.size == 10
    assert len(p1_s10.items) == 10

    # Negative bounds
    pn1_sn10 = await document_service.get_page(-1, -10)

    assert isinstance(pn1_sn10, PaginatedResponse)
    assert pn1_sn10.element_count == element_count
    assert pn1_sn10.page == 1
    assert pn1_sn10.size == 1
    assert len(pn1_sn10.items) == 1

    # Page 1, size max_per_page * 10 -> max per page exceeded - should default to mpp
    p1_smppt10 = await document_service.get_page(1, max_per_page * 10)

    assert isinstance(p1_smppt10, PaginatedResponse)
    assert p1_smppt10.element_count == element_count
    assert p1_smppt10.page == 1
    assert p1_smppt10.size == max_per_page
    assert len(p1_smppt10.items) == max_per_page

    # Page (count/mpp)*100, size max_per_page -> out of bounds - should return no items
    out_of_bounds_page = int((element_count/max_per_page) * 100)
    p100_sct10 = await document_service.get_page(out_of_bounds_page, max_per_page)

    assert isinstance(p100_sct10, PaginatedResponse)
    assert p100_sct10.element_count == element_count
    assert p100_sct10.page == out_of_bounds_page
    assert p100_sct10.size == max_per_page
    assert len(p100_sct10.items) == 0



