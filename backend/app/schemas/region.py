from pydantic import BaseModel


class RegionCategorySummary(BaseModel):
    name: str
    count: int


class RegionSummary(BaseModel):
    region: str
    total: int
    categories: list[RegionCategorySummary]
