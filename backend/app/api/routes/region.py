from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas.region import (
    RegionCategoryResponse,
    RegionCategorySummary,
    RegionDistrictSummary,
    RegionPlace,
    RegionSummary,
)
from app.services.seoul_data import seoul_data_store

router = APIRouter(prefix="/region", tags=["region"])

SEOUL_DISTRICTS = (
    "종로구",
    "중구",
    "용산구",
    "성동구",
    "광진구",
    "동대문구",
    "중랑구",
    "성북구",
    "강북구",
    "도봉구",
    "노원구",
    "은평구",
    "서대문구",
    "마포구",
    "양천구",
    "강서구",
    "구로구",
    "금천구",
    "영등포구",
    "동작구",
    "관악구",
    "서초구",
    "강남구",
    "송파구",
    "강동구",
)


def _district_from_address(address: str, detail_address: str) -> str | None:
    full_address = f"{address} {detail_address}"
    return next((district for district in SEOUL_DISTRICTS if district in full_address), None)


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
    district: Annotated[str | None, Query()] = None,
) -> RegionCategoryResponse:
    if not seoul_data_store.loaded:
        raise HTTPException(status_code=503, detail="서울 지역 데이터를 불러오지 못했습니다.")

    valid_categories = {item.name for item in seoul_data_store.category_counts}
    if category not in valid_categories:
        raise HTTPException(status_code=404, detail="존재하지 않는 서울 정보 카테고리입니다.")
    if district is not None and district not in SEOUL_DISTRICTS:
        raise HTTPException(status_code=400, detail="존재하지 않는 서울 자치구입니다.")

    category_items = [item for item in seoul_data_store.items if item.category == category]
    district_counts = {name: 0 for name in SEOUL_DISTRICTS}
    for item in category_items:
        item_district = _district_from_address(item.address, item.detail_address)
        if item_district:
            district_counts[item_district] += 1

    filtered_items = category_items
    if district:
        filtered_items = [
            item
            for item in category_items
            if _district_from_address(item.address, item.detail_address) == district
        ]

    total = len(filtered_items)
    start = (page - 1) * size
    page_items = filtered_items[start : start + size]

    return RegionCategoryResponse(
        category=category,
        district=district,
        districts=[
            RegionDistrictSummary(name=name, count=district_counts[name])
            for name in SEOUL_DISTRICTS
        ],
        all_total=len(category_items),
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
