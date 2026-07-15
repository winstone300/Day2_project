from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.session import check_database_connection
from app.services.seoul_data import seoul_data_store

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> JSONResponse:
    database_connected = check_database_connection()
    region_data_loaded = seoul_data_store.loaded
    status_code = 200 if database_connected and region_data_loaded else 503
    content: dict[str, str | int] = {
        "status": "ok" if status_code == 200 else "error",
        "database": "connected" if database_connected else "disconnected",
        "region_data": "loaded" if region_data_loaded else "error",
        "region_items": seoul_data_store.total,
        "region_categories": len(seoul_data_store.category_counts),
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
    )
