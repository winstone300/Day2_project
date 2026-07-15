from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10_000)
    edit_password: str = Field(min_length=1, max_length=100)

    @field_validator("title", "content", "edit_password")
    @classmethod
    def reject_blank_values(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return stripped_value


class PostUpdate(PostCreate):
    pass


class PasswordRequest(BaseModel):
    edit_password: str = Field(min_length=1, max_length=100)


class PasswordVerification(BaseModel):
    verified: bool


class PostSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region: str
    title: str
    view_count: int
    created_at: datetime
    updated_at: datetime


class PostDetail(PostSummary):
    content: str


PostSort = Literal["latest", "views"]


class PostListResponse(BaseModel):
    items: list[PostSummary]
    total: int
    page: int
    size: int
    total_pages: int
