# uv run uvicorn main:app --reload --reload-dir api --app-dir api --env-file .env

from fastapi import FastAPI

from contextlib import asynccontextmanager

from repositories.factory import RepositoryFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    await RepositoryFactory.setup()

    yield

    await RepositoryFactory.teardown()

app = FastAPI(lifespan=lifespan)

app.root_path = "/api"

from apps.testapp.router import router as testapp_router
app.include_router(testapp_router, prefix="/testapp")

from apps.auth.router import router as auth_router
app.include_router(auth_router, prefix="/auth")

from apps.job_listing.router import router as listing_router
app.include_router(listing_router, prefix="/listing")