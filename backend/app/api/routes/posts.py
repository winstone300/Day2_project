from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.post import Post
from app.schemas.post import (
    PasswordRequest,
    PasswordVerification,
    PostCreate,
    PostDetail,
    PostListResponse,
    PostSort,
    PostSummary,
    PostUpdate,
)
from app.services import post_service

router = APIRouter(prefix="/posts", tags=["posts"])


def _get_post_or_404(database: Session, post_id: int) -> Post:
    post = post_service.get_post(database, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


def _verify_password(post: Post, edit_password: str) -> None:
    if not post_service.password_matches(post, edit_password):
        raise HTTPException(status_code=403, detail="수정용 비밀번호가 일치하지 않습니다.")


@router.get("", response_model=PostListResponse)
def list_posts(
    database: Session = Depends(get_db),
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    query: Annotated[str | None, Query(max_length=200)] = None,
    sort: Annotated[PostSort, Query()] = "latest",
) -> PostListResponse:
    normalized_query = query.strip() if query and query.strip() else None
    posts, total = post_service.get_posts(
        database,
        page=page,
        size=size,
        query=normalized_query,
        sort=sort,
    )
    return PostListResponse(
        items=[PostSummary.model_validate(post) for post in posts],
        total=total,
        page=page,
        size=size,
        total_pages=(total + size - 1) // size,
    )


@router.get("/{post_id}", response_model=PostDetail)
def get_post(post_id: int, database: Session = Depends(get_db)) -> Post:
    post = post_service.get_post_and_increment_view(database, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post


@router.post("", response_model=PostDetail, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, database: Session = Depends(get_db)) -> Post:
    return post_service.create_post(database, payload)


@router.post("/{post_id}/verify-password", response_model=PasswordVerification)
def verify_post_password(
    post_id: int,
    payload: PasswordRequest,
    database: Session = Depends(get_db),
) -> PasswordVerification:
    post = _get_post_or_404(database, post_id)
    _verify_password(post, payload.edit_password)
    return PasswordVerification(verified=True)


@router.put("/{post_id}", response_model=PostDetail)
def update_post(
    post_id: int,
    payload: PostUpdate,
    database: Session = Depends(get_db),
) -> Post:
    post = _get_post_or_404(database, post_id)
    _verify_password(post, payload.edit_password)
    return post_service.update_post(database, post, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    payload: PasswordRequest,
    database: Session = Depends(get_db),
) -> Response:
    post = _get_post_or_404(database, post_id)
    _verify_password(post, payload.edit_password)
    post_service.delete_post(database, post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
