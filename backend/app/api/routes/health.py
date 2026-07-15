from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> JSONResponse:
    if not check_database_connection():
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "database": "disconnected",
                "region_data": "not_loaded",
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "database": "connected",
            "region_data": "not_loaded",
        },
    )
