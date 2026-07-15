import unittest

from fastapi import HTTPException

from app.api.routes.chat import chat
from app.schemas.chat import ChatRequest
from app.services.chat_service import answer_region_question
from app.services.seoul_data import SeoulDataStore, seoul_data_store


class ChatApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not seoul_data_store.loaded:
            seoul_data_store.load()

    def test_finds_place_by_exact_title(self) -> None:
        response = chat(ChatRequest(message="양화한강공원 주소 알려줘"))

        self.assertEqual(response.intent, "region_info")
        self.assertEqual(response.results[0].title, "양화한강공원")
        self.assertIn("영등포구", response.results[0].address)
        self.assertIn("양화한강공원", response.answer)

    def test_filters_by_category_and_honors_result_limit(self) -> None:
        response = chat(ChatRequest(message="서울 축제 추천해줘", max_results=2))

        self.assertEqual(len(response.results), 2)
        self.assertTrue(all(item.category == "축제공연행사" for item in response.results))

    def test_returns_helpful_answer_when_no_place_matches(self) -> None:
        response = chat(ChatRequest(message="화성 우주정거장 견학"))

        self.assertEqual(response.results, [])
        self.assertIn("찾지 못했어요", response.answer)

    def test_rejects_request_when_region_data_is_not_loaded(self) -> None:
        original_loaded = seoul_data_store.loaded
        seoul_data_store.loaded = False
        try:
            with self.assertRaises(HTTPException) as context:
                chat(ChatRequest(message="관광지 추천"))
        finally:
            seoul_data_store.loaded = original_loaded

        self.assertEqual(context.exception.status_code, 503)

    def test_service_is_deterministic(self) -> None:
        first = answer_region_question("강남 문화시설", 3, seoul_data_store)
        second = answer_region_question("강남 문화시설", 3, seoul_data_store)
        self.assertEqual(first, second)

    def test_empty_store_returns_no_results(self) -> None:
        empty_store = SeoulDataStore(seoul_data_store.data_dir)
        response = answer_region_question("관광지 추천", 3, empty_store)
        self.assertEqual(response.results, [])
