from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    max_results: int = Field(default=3, ge=1, le=5)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        message = value.strip()
        if not message:
            raise ValueError("질문을 입력해 주세요.")
        return message


class ChatPlaceResult(BaseModel):
    content_id: str
    title: str
    category: str
    address: str
    telephone: str
    longitude: float | None
    latitude: float | None
    image_url: str


class ChatPostResult(BaseModel):
    id: int
    title: str
    content_preview: str
    view_count: int
    created_at: datetime


class ChatResponse(BaseModel):
    answer: str
    intent: Literal["region_info", "post_search"] = "region_info"
    results: list[ChatPlaceResult] = Field(default_factory=list)
    post_results: list[ChatPostResult] = Field(default_factory=list)
    source: str = "한국관광공사 TourAPI 4.0 서울 데이터"
