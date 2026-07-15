import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.config import settings

SEOUL_DATA_FILES = (
    ("서울_관광지.json", "관광지", "12"),
    ("서울_레포츠.json", "레포츠", "28"),
    ("서울_문화시설.json", "문화시설", "14"),
    ("서울_쇼핑.json", "쇼핑", "38"),
    ("서울_숙박.json", "숙박", "32"),
    ("서울_여행코스.json", "여행코스", "25"),
    ("서울_축제공연행사.json", "축제공연행사", "15"),
)


class SeoulDataError(RuntimeError):
    """서울 원본 데이터가 없거나 스키마 검증에 실패했을 때 발생한다."""


@dataclass(frozen=True, slots=True)
class SeoulPlace:
    content_id: str
    content_type_id: str
    category: str
    title: str
    address: str
    detail_address: str
    telephone: str
    longitude: float | None
    latitude: float | None
    image_url: str
    classification_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CategoryCount:
    name: str
    count: int


def _text(value: Any) -> str:
    return str(value or "").strip()


def _coordinate(value: Any) -> float | None:
    raw_value = _text(value)
    if not raw_value:
        return None

    try:
        return float(raw_value)
    except ValueError:
        return None


class SeoulDataStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.items: tuple[SeoulPlace, ...] = ()
        self.category_counts: tuple[CategoryCount, ...] = ()
        self.loaded = False
        self.error: str | None = None

    @property
    def total(self) -> int:
        return len(self.items)

    def load(self) -> None:
        loaded_items: list[SeoulPlace] = []
        category_counts: list[CategoryCount] = []
        self.loaded = False
        self.error = None

        try:
            for filename, expected_category, expected_type_id in SEOUL_DATA_FILES:
                document = self._read_document(filename)
                category = _text(document.get("contentType"))
                content_type_id = _text(document.get("contentTypeId"))
                rows = document.get("items")

                if category != expected_category or content_type_id != expected_type_id:
                    raise SeoulDataError(f"{filename}: 콘텐츠 유형 정보가 예상값과 다릅니다.")
                if not isinstance(rows, list):
                    raise SeoulDataError(f"{filename}: items가 배열이 아닙니다.")

                declared_total = document.get("total")
                if not isinstance(declared_total, int) or declared_total != len(rows):
                    raise SeoulDataError(f"{filename}: total과 실제 항목 수가 다릅니다.")

                loaded_items.extend(
                    self._normalize_item(row, expected_category, expected_type_id, filename)
                    for row in rows
                )
                category_counts.append(CategoryCount(name=expected_category, count=len(rows)))
        except (OSError, json.JSONDecodeError, SeoulDataError) as exc:
            self.items = ()
            self.category_counts = ()
            self.error = str(exc)
            raise SeoulDataError(str(exc)) from exc

        self.items = tuple(loaded_items)
        self.category_counts = tuple(category_counts)
        self.loaded = True

    def _read_document(self, filename: str) -> dict[str, Any]:
        file_path = self.data_dir / filename
        if not file_path.is_file():
            raise SeoulDataError(f"필수 데이터 파일이 없습니다: {filename}")

        with file_path.open(encoding="utf-8") as file:
            document = json.load(file)

        if not isinstance(document, dict) or _text(document.get("region")) != "서울":
            raise SeoulDataError(f"{filename}: 서울 데이터 문서가 아닙니다.")
        return document

    @staticmethod
    def _normalize_item(
        row: Any,
        category: str,
        expected_type_id: str,
        filename: str,
    ) -> SeoulPlace:
        if not isinstance(row, dict):
            raise SeoulDataError(f"{filename}: 항목이 객체가 아닙니다.")

        content_id = _text(row.get("contentid"))
        title = _text(row.get("title"))
        if not content_id or not title:
            raise SeoulDataError(f"{filename}: contentid 또는 title이 비어 있습니다.")

        content_type_id = _text(row.get("contenttypeid")) or expected_type_id
        if content_type_id != expected_type_id:
            raise SeoulDataError(f"{filename}: 항목의 콘텐츠 유형이 예상값과 다릅니다.")

        classification_codes = tuple(
            code
            for key in ("cat1", "cat2", "cat3", "lclsSystm1", "lclsSystm2", "lclsSystm3")
            if (code := _text(row.get(key)))
        )

        return SeoulPlace(
            content_id=content_id,
            content_type_id=content_type_id,
            category=category,
            title=title,
            address=_text(row.get("addr1")),
            detail_address=_text(row.get("addr2")),
            telephone=_text(row.get("tel")),
            longitude=_coordinate(row.get("mapx")),
            latitude=_coordinate(row.get("mapy")),
            image_url=_text(row.get("firstimage")),
            classification_codes=classification_codes,
        )


seoul_data_store = SeoulDataStore(settings.seoul_data_dir)
