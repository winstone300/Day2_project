from sqlalchemy import func, select

from app.db.session import Base, SessionLocal, engine
from app.models.post import Post


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as database:
        post_count = database.scalar(select(func.count(Post.id))) or 0
        if post_count > 0:
            return

        database.add(
            Post(
                region="서울",
                title="LocalHub 서울 커뮤니티에 오신 것을 환영합니다",
                content="서울의 관광지와 지역 정보를 자유롭게 공유해 주세요.",
                edit_password="localhub-demo",
            )
        )
        database.commit()
