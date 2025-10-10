# uv run uvicorn main:app --reload --reload-dir src --app-dir src --env-file .env

from fastapi import FastAPI

from apps.testapp.router import router as testapp_router
from apps.auth.router import router as auth_router

app = FastAPI()

app.include_router(testapp_router, prefix="/testapp")
app.include_router(auth_router, prefix="/auth")