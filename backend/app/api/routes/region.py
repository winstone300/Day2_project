from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas.region import (
    RegionCategoryResponse,
    RegionCategorySummary,
    RegionPlace,
    RegionSummary,
)
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


@router.get("/categories/{category}", response_model=RegionCategoryResponse)
def get_region_category(
    category: str,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
) -> RegionCategoryResponse:
    if not seoul_data_store.loaded:
        raise HTTPException(status_code=503, detail="서울 지역 데이터를 불러오지 못했습니다.")

    valid_categories = {item.name for item in seoul_data_store.category_counts}
    if category not in valid_categories:
        raise HTTPException(status_code=404, detail="존재하지 않는 서울 정보 카테고리입니다.")

    category_items = [item for item in seoul_data_store.items if item.category == category]
    total = len(category_items)
    start = (page - 1) * size
    page_items = category_items[start : start + size]

    return RegionCategoryResponse(
        category=category,
        items=[
            RegionPlace(
                content_id=item.content_id,
                title=item.title,
                category=item.category,
                address=" ".join(part for part in (item.address, item.detail_address) if part),
                telephone=item.telephone,
                longitude=item.longitude,
                latitude=item.latitude,
                image_url=item.image_url,
            )
            for item in page_items
        ],
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size,
    )
