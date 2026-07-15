from pydantic import BaseModel


class RegionCategorySummary(BaseModel):
    name: str
    count: int


class RegionSummary(BaseModel):
    region: str
    total: int
    categories: list[RegionCategorySummary]


class RegionPlace(BaseModel):
    content_id: str
    title: str
    category: str
    address: str
    telephone: str
    longitude: float | None
    latitude: float | None
    image_url: str


class RegionCategoryResponse(BaseModel):
    category: str
    items: list[RegionPlace]
    total: int
    page: int
    size: int
    total_pages: int
