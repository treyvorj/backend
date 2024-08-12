from fastapi import APIRouter
from app.api.routes import sites

api_router: APIRouter = APIRouter()

api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
