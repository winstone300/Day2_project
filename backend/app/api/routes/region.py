from fastapi import APIRouter, HTTPException

from app.schemas.region import RegionCategorySummary, RegionSummary
from app.services.seoul_data import seoul_data_store

router = APIRouter(prefix="/region", tags=["region"])


@router.get("/summary", response_model=RegionSummary)
def get_region_summary() -> RegionSummary:
    if not seoul_data_store.loaded:
        raise HTTPException(status_code=503, detail="서울 지역 데이터를 불러오지 못했습니다.")

    return RegionSummary(
        region="서울",
        total=seoul_data_store.total,
        categories=[
            RegionCategorySummary(name=category.name, count=category.count)
            for category in seoul_data_store.category_counts
        ],
    )
