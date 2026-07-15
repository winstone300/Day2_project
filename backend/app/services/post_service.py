from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


def get_posts(database: Session) -> list[Post]:
    statement = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    return list(database.scalars(statement).all())


def get_post(database: Session, post_id: int) -> Post | None:
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
    database.commit()
    database.refresh(post)
    return post


def delete_post(database: Session, post: Post) -> None:
    database.delete(post)
    database.commit()
