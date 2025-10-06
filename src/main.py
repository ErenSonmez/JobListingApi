# uv run uvicorn main:app --reload --env-file ../.env

from fastapi import FastAPI

from apps.testapp.router import router as testapp_router

app = FastAPI()

app.include_router(testapp_router, prefix="/testapp")