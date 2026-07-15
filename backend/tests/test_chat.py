import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.chat import chat
from app.db.session import Base
from app.models.post import Post
from app.schemas.chat import ChatRequest
from app.services.chat_service import answer_region_question
from app.services.seoul_data import SeoulDataStore, seoul_data_store


class ChatApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not seoul_data_store.loaded:
            seoul_data_store.load()

    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "chat.db"
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

    def _add_post(self, title: str, content: str) -> Post:
        post = Post(
            region="서울",
            title=title,
            content=content,
            edit_password="chat-test",
        )
        self.database.add(post)
        self.database.commit()
        self.database.refresh(post)
        return post

    def test_finds_place_by_exact_title(self) -> None:
        response = chat(ChatRequest(message="양화한강공원 주소 알려줘"), self.database)

        self.assertEqual(response.intent, "region_info")
        self.assertEqual(response.results[0].title, "양화한강공원")
        self.assertIn("영등포구", response.results[0].address)
        self.assertIn("양화한강공원", response.answer)

    def test_filters_by_category_and_honors_result_limit(self) -> None:
        response = chat(ChatRequest(message="서울 축제 추천해줘", max_results=2), self.database)

        self.assertEqual(len(response.results), 2)
        self.assertTrue(all(item.category == "축제공연행사" for item in response.results))

    def test_returns_helpful_answer_when_no_place_matches(self) -> None:
        response = chat(ChatRequest(message="화성 우주정거장 견학"), self.database)

        self.assertEqual(response.results, [])
        self.assertIn("찾지 못했어요", response.answer)

    def test_rejects_request_when_region_data_is_not_loaded(self) -> None:
        original_loaded = seoul_data_store.loaded
        seoul_data_store.loaded = False
        try:
            with self.assertRaises(HTTPException) as context:
                chat(ChatRequest(message="관광지 추천"), self.database)
        finally:
            seoul_data_store.loaded = original_loaded

        self.assertEqual(context.exception.status_code, 503)

    def test_service_is_deterministic(self) -> None:
        first = answer_region_question("강남 문화시설", 3, seoul_data_store)
        second = answer_region_question("강남 문화시설", 3, seoul_data_store)
        self.assertEqual(first, second)
        self.assertTrue(all(item.category == "문화시설" for item in first.results))

    def test_empty_store_returns_no_results(self) -> None:
        empty_store = SeoulDataStore(seoul_data_store.data_dir)
        response = answer_region_question("관광지 추천", 3, empty_store)
        self.assertEqual(response.results, [])

    def test_searches_community_posts(self) -> None:
        matching_post = self._add_post("한강 야경 후기", "반포한강공원에 다녀왔습니다.")
        self._add_post("서울 전시 소식", "미술관 전시를 소개합니다.")

        response = chat(
            ChatRequest(message="게시판에서 한강 검색해줘", max_results=3),
            self.database,
        )

        self.assertEqual(response.intent, "post_search")
        self.assertEqual(response.results, [])
        self.assertEqual(len(response.post_results), 1)
        self.assertEqual(response.post_results[0].id, matching_post.id)
        self.assertEqual(response.source, "LocalHub 서울 커뮤니티")

    def test_returns_recent_posts_without_keyword(self) -> None:
        self._add_post("첫 번째 글", "첫 번째 내용")
        latest_post = self._add_post("두 번째 글", "두 번째 내용")

        response = chat(ChatRequest(message="최근 커뮤니티 글 보여줘"), self.database)

        self.assertEqual(response.intent, "post_search")
        self.assertEqual(response.post_results[0].id, latest_post.id)
        self.assertIn("최근 게시글", response.answer)

    def test_returns_empty_post_search_result(self) -> None:
        response = chat(ChatRequest(message="게시글에서 우주정거장 찾아줘"), self.database)

        self.assertEqual(response.intent, "post_search")
        self.assertEqual(response.post_results, [])
        self.assertIn("찾지 못했어요", response.answer)
