import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base, get_db
from app.main import app


class ApiIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "integration.db"
        self.engine = create_engine(
            f"sqlite:///{database_path.as_posix()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=self.engine)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

        def override_database():
            database: Session = self.session_factory()
            try:
                yield database
            finally:
                database.close()

        app.dependency_overrides[get_db] = override_database
        self.client_context = TestClient(app)
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        app.dependency_overrides.clear()
        self.engine.dispose()
        self.temporary_directory.cleanup()

    def _create_post(
        self,
        *,
        title: str = "한강 산책 후기",
        content: str = "반포한강공원에서 야경을 봤습니다.",
        password: str = "integration-password",
    ) -> dict:
        response = self.client.post(
            "/api/posts",
            json={
                "title": title,
                "content": content,
                "edit_password": password,
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_post_crud_and_password_errors_over_http(self) -> None:
        created = self._create_post()
        post_id = created["id"]

        detail = self.client.get(f"/api/posts/{post_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["view_count"], 1)

        wrong_password = self.client.post(
            f"/api/posts/{post_id}/verify-password",
            json={"edit_password": "wrong-password"},
        )
        self.assertEqual(wrong_password.status_code, 403)
        self.assertEqual(wrong_password.json()["detail"], "수정용 비밀번호가 일치하지 않습니다.")

        updated = self.client.put(
            f"/api/posts/{post_id}",
            json={
                "title": "수정된 한강 산책 후기",
                "content": "수정된 게시글 내용입니다.",
                "edit_password": "integration-password",
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["title"], "수정된 한강 산책 후기")

        deleted = self.client.request(
            "DELETE",
            f"/api/posts/{post_id}",
            json={"edit_password": "integration-password"},
        )
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(self.client.get(f"/api/posts/{post_id}").status_code, 404)

    def test_post_search_pagination_and_view_sort_over_http(self) -> None:
        first = self._create_post(title="한강 야경", content="한강 산책 정보")
        self._create_post(title="서울 전시", content="미술관 전시 정보")

        self.client.get(f"/api/posts/{first['id']}")
        self.client.get(f"/api/posts/{first['id']}")

        search = self.client.get("/api/posts", params={"query": "한강", "page": 1, "size": 1})
        self.assertEqual(search.status_code, 200)
        self.assertEqual(search.json()["total"], 1)
        self.assertEqual(search.json()["items"][0]["id"], first["id"])

        popular = self.client.get("/api/posts", params={"sort": "views"})
        self.assertEqual(popular.status_code, 200)
        self.assertEqual(popular.json()["items"][0]["id"], first["id"])
        self.assertEqual(popular.json()["items"][0]["view_count"], 2)

    def test_region_and_community_chat_over_http(self) -> None:
        post = self._create_post()

        region_chat = self.client.post(
            "/api/chat",
            json={"message": "강남 문화시설 알려줘", "max_results": 2},
        )
        self.assertEqual(region_chat.status_code, 200)
        self.assertEqual(region_chat.json()["intent"], "region_info")
        self.assertEqual(len(region_chat.json()["results"]), 2)
        self.assertTrue(
            all(result["category"] == "문화시설" for result in region_chat.json()["results"])
        )

        post_chat = self.client.post(
            "/api/chat",
            json={"message": "게시판에서 한강 검색해줘"},
        )
        self.assertEqual(post_chat.status_code, 200)
        self.assertEqual(post_chat.json()["intent"], "post_search")
        self.assertEqual(post_chat.json()["post_results"][0]["id"], post["id"])

    def test_region_category_page_over_http(self) -> None:
        response = self.client.get(
            "/api/region/categories/관광지",
            params={"page": 2, "size": 10},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "관광지")
        self.assertEqual(response.json()["page"], 2)
        self.assertEqual(len(response.json()["items"]), 10)
        self.assertEqual(response.json()["total"], 783)
        self.assertEqual(
            self.client.get("/api/region/categories/음식점").status_code,
            404,
        )

    def test_validation_errors_are_returned_as_422(self) -> None:
        invalid_requests = (
            self.client.post(
                "/api/posts",
                json={"title": " ", "content": "내용", "edit_password": "password"},
            ),
            self.client.get("/api/posts", params={"page": 0}),
            self.client.post("/api/chat", json={"message": " "}),
            self.client.post("/api/chat", json={"message": "서울 관광지", "max_results": 6}),
        )
        self.assertTrue(all(response.status_code == 422 for response in invalid_requests))

    def test_cors_allows_only_configured_frontend(self) -> None:
        allowed = self.client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(
            allowed.headers.get("access-control-allow-origin"),
            "http://localhost:5173",
        )

        denied = self.client.options(
            "/api/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        self.assertNotIn("access-control-allow-origin", denied.headers)
