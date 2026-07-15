import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.posts import (
    create_post,
    delete_post,
    get_post,
    list_posts,
    update_post,
    verify_post_password,
)
from app.db.session import Base
from app.models.post import Post
from app.schemas.post import PasswordRequest, PostCreate, PostDetail, PostUpdate


class PostCrudTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "posts.db"
        self.engine = create_engine(
            f"sqlite:///{database_path.as_posix()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.database: Session = self.session_factory()

    def tearDown(self) -> None:
        self.database.close()
        self.engine.dispose()
        self.temporary_directory.cleanup()

    def _create_post(
        self,
        password: str = "demo-password",
        title: str = "서울 여행 정보를 공유합니다",
        content: str = "한강공원 방문 후기를 공유합니다.",
    ) -> Post:
        return create_post(
            PostCreate(
                title=title,
                content=content,
                edit_password=password,
            ),
            self.database,
        )

    def test_create_list_detail_and_persistence(self) -> None:
        created = self._create_post()
        self.assertEqual(created.region, "서울")
        self.assertEqual(created.view_count, 0)
        self.assertNotIn("edit_password", PostDetail.model_validate(created).model_dump())
        post_list = list_posts(self.database)
        self.assertEqual(post_list.total, 1)
        self.assertEqual(len(post_list.items), 1)
        self.assertEqual(get_post(created.id, self.database).title, created.title)

        self.database.close()
        self.database = self.session_factory()
        persisted = self.database.get(Post, created.id)
        self.assertEqual(persisted.content, "한강공원 방문 후기를 공유합니다.")
        self.assertEqual(persisted.view_count, 1)

    def test_verify_update_and_delete_with_correct_password(self) -> None:
        created = self._create_post()
        verification = verify_post_password(
            created.id,
            PasswordRequest(edit_password="demo-password"),
            self.database,
        )
        self.assertTrue(verification.verified)

        updated = update_post(
            created.id,
            PostUpdate(
                title="수정된 서울 여행 정보",
                content="수정된 방문 후기입니다.",
                edit_password="demo-password",
            ),
            self.database,
        )
        self.assertEqual(updated.title, "수정된 서울 여행 정보")

        response = delete_post(
            created.id,
            PasswordRequest(edit_password="demo-password"),
            self.database,
        )
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(self.database.get(Post, created.id))

    def test_rejects_wrong_password(self) -> None:
        created = self._create_post()

        with self.assertRaises(HTTPException) as verify_context:
            verify_post_password(
                created.id,
                PasswordRequest(edit_password="wrong-password"),
                self.database,
            )
        self.assertEqual(verify_context.exception.status_code, 403)

        with self.assertRaises(HTTPException) as update_context:
            update_post(
                created.id,
                PostUpdate(
                    title="수정 시도",
                    content="수정되면 안 됩니다.",
                    edit_password="wrong-password",
                ),
                self.database,
            )
        self.assertEqual(update_context.exception.status_code, 403)

        with self.assertRaises(HTTPException) as delete_context:
            delete_post(
                created.id,
                PasswordRequest(edit_password="wrong-password"),
                self.database,
            )
        self.assertEqual(delete_context.exception.status_code, 403)
        self.assertIsNotNone(self.database.get(Post, created.id))

    def test_returns_404_for_missing_post(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_post(9999, self.database)
        self.assertEqual(context.exception.status_code, 404)

    def test_searches_title_and_content_with_pagination(self) -> None:
        first = self._create_post(title="한강 관광 후기", content="야경이 멋집니다.")
        second = self._create_post(title="서울 숙박 정보", content="종로 호텔 후기입니다.")
        third = self._create_post(title="축제 정보", content="한강에서 열리는 행사입니다.")

        first_page = list_posts(self.database, page=1, size=2)
        self.assertEqual(first_page.total, 3)
        self.assertEqual(first_page.total_pages, 2)
        self.assertEqual([item.id for item in first_page.items], [third.id, second.id])

        second_page = list_posts(self.database, page=2, size=2)
        self.assertEqual([item.id for item in second_page.items], [first.id])

        out_of_range_page = list_posts(self.database, page=3, size=2)
        self.assertEqual(out_of_range_page.total, 3)
        self.assertEqual(out_of_range_page.items, [])

        title_results = list_posts(self.database, query="숙박")
        self.assertEqual(title_results.total, 1)
        self.assertEqual(title_results.items[0].id, second.id)

        content_results = list_posts(self.database, query="한강")
        self.assertEqual(content_results.total, 2)
        self.assertEqual({item.id for item in content_results.items}, {first.id, third.id})

        empty_results = list_posts(self.database, query="없는 검색어")
        self.assertEqual(empty_results.total, 0)
        self.assertEqual(empty_results.items, [])

        blank_query_results = list_posts(self.database, query="   ")
        self.assertEqual(blank_query_results.total, 3)

    def test_increments_views_and_sorts_by_view_count(self) -> None:
        first = self._create_post(title="첫 번째 게시글")
        second = self._create_post(title="두 번째 게시글")
        original_updated_at = second.updated_at

        self.assertEqual(get_post(first.id, self.database).view_count, 1)
        self.assertEqual(get_post(second.id, self.database).view_count, 1)
        self.assertEqual(get_post(second.id, self.database).view_count, 2)

        popular_posts = list_posts(self.database, sort="views")
        self.assertEqual([item.id for item in popular_posts.items], [second.id, first.id])
        self.assertEqual(popular_posts.items[0].view_count, 2)
        self.assertEqual(self.database.get(Post, second.id).updated_at, original_updated_at)


if __name__ == "__main__":
    unittest.main()
