import asyncio

from models.job_listing import JobListing
from models.user import User

from repositories.factory import RepositoryFactory
from repositories.job_listing import JobListingRepository
from repositories.schemas import MongoClientCredentials, OrderByField

from beanie.odm.operators.find.evaluation import Text

from services.auth import AuthService

from fastapi import APIRouter, Depends, UploadFile

from typing import Annotated

from services.factory import ServiceFactory

router = APIRouter(tags=["Test app"])

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"

@router.post("/reset-db-credentials")
async def reset_db_credentials(creds: MongoClientCredentials):
    await RepositoryFactory.set_db_credentials(creds)
    return creds

@router.get("/auth-test")
async def auth_test(user: Annotated[User, Depends(AuthService.get_user_from_token)]):
    return {"user": user}

@router.post("/upload-test")
async def upload_test(file: UploadFile):
    return {
        "filename": file.filename,
        "headers": file.headers,
        "content-type": file.content_type,
        "size": file.size,
        "content": (await file.read()).decode()
    }

@router.get("/repo-filter-test")
async def repo_filter_test():
    service = ServiceFactory.get_job_listing_service()
    return await service.get_page(1, 10,
        filter_mappings=[
        Text('"developer" -"Full Stack"', case_sensitive=False),

    ],
    order_by=[OrderByField(field_name = "date_posted", ascending = True)]
    )
