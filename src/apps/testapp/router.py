import asyncio

from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
async def ping():
    await asyncio.sleep(10)
    return "pong"