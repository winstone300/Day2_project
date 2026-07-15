import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException

from app.api.routes.health import health_check
from app.api.routes.region import get_region_category, get_region_summary
from app.core.config import settings
from app.services.seoul_data import (
    SEOUL_DATA_FILES,
    SeoulDataError,
    SeoulDataStore,
    seoul_data_store,
)


class SeoulDataStoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.store = SeoulDataStore(settings.seoul_data_dir)
        cls.store.load()

    def test_loads_expected_total_and_categories(self) -> None:
        self.assertEqual(self.store.total, 6518)
        self.assertEqual(len(self.store.category_counts), 7)
        self.assertEqual(
            {category.name: category.count for category in self.store.category_counts},
            {
                "관광지": 783,
                "레포츠": 126,
                "문화시설": 566,
                "쇼핑": 4368,
                "숙박": 423,
                "여행코스": 51,
                "축제공연행사": 201,
            },
        )

    def test_normalizes_ids_and_coordinates(self) -> None:
        self.assertTrue(all(isinstance(item.content_id, str) for item in self.store.items))
        self.assertTrue(all(isinstance(item.content_type_id, str) for item in self.store.items))
        self.assertTrue(all(item.longitude is not None for item in self.store.items))
        self.assertTrue(all(item.latitude is not None for item in self.store.items))

    def test_keeps_missing_travel_course_addresses_empty(self) -> None:
        travel_courses = [item for item in self.store.items if item.category == "여행코스"]
        self.assertEqual(len(travel_courses), 51)
        self.assertTrue(all(item.address == "" for item in travel_courses))

    def test_expected_source_files_exist(self) -> None:
        self.assertEqual(len(SEOUL_DATA_FILES), 7)
        self.assertTrue(
            all((settings.seoul_data_dir / filename).is_file() for filename, _, _ in SEOUL_DATA_FILES)
        )

    def test_missing_source_file_is_reported_without_partial_data(self) -> None:
        with TemporaryDirectory() as directory:
            empty_store = SeoulDataStore(Path(directory))
            with self.assertRaises(SeoulDataError):
                empty_store.load()

        self.assertFalse(empty_store.loaded)
        self.assertEqual(empty_store.total, 0)
        self.assertIsNotNone(empty_store.error)


class RegionApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        seoul_data_store.load()

    def test_region_summary(self) -> None:
        summary = get_region_summary()
        self.assertEqual(summary.region, "서울")
        self.assertEqual(summary.total, 6518)
        self.assertEqual(len(summary.categories), 7)

    def test_region_category_is_paginated_by_ten(self) -> None:
        first_page = get_region_category("관광지", page=1, size=10)
        second_page = get_region_category("관광지", page=2, size=10)

        self.assertEqual(first_page.total, 783)
        self.assertEqual(first_page.total_pages, 79)
        self.assertEqual(len(first_page.items), 10)
        self.assertEqual(len(second_page.items), 10)
        self.assertNotEqual(first_page.items[0].content_id, second_page.items[0].content_id)

    def test_unknown_region_category_returns_404(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_region_category("음식점", page=1, size=10)
        self.assertEqual(context.exception.status_code, 404)

    def test_health_reports_loaded_data(self) -> None:
        response = health_check()
        body = json.loads(response.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["region_data"], "loaded")
        self.assertEqual(body["region_items"], 6518)
        self.assertEqual(body["region_categories"], 7)


if __name__ == "__main__":
    unittest.main()
