from fastapi import APIRouter
from app.api.scan import scan_router

api_router = APIRouter(prefix="/api")

@api_router.get("/ping")
async def ping():
    return {"message": "pong"}

api_router.include_router(scan_router)
