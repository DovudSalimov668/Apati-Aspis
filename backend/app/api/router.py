from fastapi import APIRouter
from app.api.scan import scan_router
from app.api.checkup import checkup_router
from app.api.history import history_router
from app.api.password import password_router

api_router = APIRouter(prefix="/api")

@api_router.get("/ping")
def ping():
    return {"message": "pong"}

api_router.include_router(scan_router)
api_router.include_router(checkup_router)
api_router.include_router(history_router)
api_router.include_router(password_router)
