from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.posts import router as posts_router
from app.api.routes.region import router as region_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(region_router)
api_router.include_router(posts_router)
