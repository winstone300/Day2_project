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

    def _create_post(self, password: str = "demo-password") -> Post:
        return create_post(
            PostCreate(
                title="서울 여행 정보를 공유합니다",
                content="한강공원 방문 후기를 공유합니다.",
                edit_password=password,
            ),
            self.database,
        )

    def test_create_list_detail_and_persistence(self) -> None:
        created = self._create_post()
        self.assertEqual(created.region, "서울")
        self.assertEqual(created.view_count, 0)
        self.assertNotIn("edit_password", PostDetail.model_validate(created).model_dump())
        self.assertEqual(len(list_posts(self.database)), 1)
        self.assertEqual(get_post(created.id, self.database).title, created.title)

        self.database.close()
        self.database = self.session_factory()
        persisted = get_post(created.id, self.database)
        self.assertEqual(persisted.content, "한강공원 방문 후기를 공유합니다.")

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


if __name__ == "__main__":
    unittest.main()
