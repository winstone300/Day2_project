from datetime import UTC, datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate, PostSort, PostUpdate


def get_posts(
    database: Session,
    *,
    page: int,
    size: int,
    query: str | None,
    sort: PostSort,
) -> tuple[list[Post], int]:
    filters = []
    if query:
        filters.append(
            or_(
                Post.title.contains(query, autoescape=True),
                Post.content.contains(query, autoescape=True),
            )
        )

    count_statement = select(func.count(Post.id)).where(*filters)
    total = database.scalar(count_statement) or 0

    if sort == "views":
        order_by = (Post.view_count.desc(), Post.created_at.desc(), Post.id.desc())
    else:
        order_by = (Post.created_at.desc(), Post.id.desc())

    statement = (
        select(Post)
        .where(*filters)
        .order_by(*order_by)
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(database.scalars(statement).all()), total


def get_post(database: Session, post_id: int) -> Post | None:
    return database.get(Post, post_id)


def get_post_and_increment_view(database: Session, post_id: int) -> Post | None:
    result = database.execute(
        update(Post)
        .where(Post.id == post_id)
        .values(view_count=Post.view_count + 1)
    )
    if result.rowcount == 0:
        database.rollback()
        return None

    database.commit()
    return database.get(Post, post_id)


def create_post(database: Session, payload: PostCreate) -> Post:
    post = Post(
        region="서울",
        title=payload.title,
        content=payload.content,
        edit_password=payload.edit_password,
    )
    database.add(post)
    database.commit()
    database.refresh(post)
    return post


def password_matches(post: Post, edit_password: str) -> bool:
    return post.edit_password == edit_password


def update_post(database: Session, post: Post, payload: PostUpdate) -> Post:
    post.title = payload.title
    post.content = payload.content
    post.updated_at = datetime.now(UTC).replace(tzinfo=None)
    database.commit()
    database.refresh(post)
    return post


def delete_post(database: Session, post: Post) -> None:
    database.delete(post)
    database.commit()
