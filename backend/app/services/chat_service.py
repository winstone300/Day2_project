import re
from dataclasses import dataclass

from app.schemas.chat import ChatPlaceResult, ChatResponse
from app.services.seoul_data import SeoulDataStore, SeoulPlace

TOKEN_PATTERN = re.compile(r"[0-9A-Za-z가-힣]+")

CATEGORY_ALIASES = {
    "관광지": ("관광", "관광지", "명소", "가볼만한곳", "볼거리"),
    "레포츠": ("레포츠", "스포츠", "체험", "레저"),
    "문화시설": ("문화", "문화시설", "박물관", "미술관", "전시"),
    "쇼핑": ("쇼핑", "시장", "백화점", "상점"),
    "숙박": ("숙박", "호텔", "숙소", "게스트하우스"),
    "여행코스": ("여행코스", "코스", "산책코스", "데이트코스"),
    "축제공연행사": ("축제", "공연", "행사", "이벤트"),
}

STOP_WORDS = {
    "서울",
    "서울시",
    "추천",
    "추천해줘",
    "알려줘",
    "알려주세요",
    "어디",
    "어디야",
    "장소",
    "정보",
    "관련",
    "있는",
    "가까운",
}


@dataclass(frozen=True, slots=True)
class ScoredPlace:
    place: SeoulPlace
    score: int


def _normalized(value: str) -> str:
    return "".join(TOKEN_PATTERN.findall(value.lower()))


def _categories_for(message: str) -> set[str]:
    normalized_message = _normalized(message)
    return {
        category
        for category, aliases in CATEGORY_ALIASES.items()
        if any(_normalized(alias) in normalized_message for alias in aliases)
    }


def _tokens_for(message: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for token in TOKEN_PATTERN.findall(message.lower()):
        normalized_token = _normalized(token)
        if len(normalized_token) < 2 or normalized_token in STOP_WORDS:
            continue
        if any(normalized_token == _normalized(alias) for aliases in CATEGORY_ALIASES.values() for alias in aliases):
            continue
        if normalized_token not in tokens:
            tokens.append(normalized_token)
    return tuple(tokens)


def _score_place(place: SeoulPlace, message: str, tokens: tuple[str, ...], categories: set[str]) -> int:
    title = _normalized(place.title)
    address = _normalized(f"{place.address} {place.detail_address}")
    normalized_message = _normalized(message)
    score = 0

    if title and title in normalized_message:
        score += 100
    if place.category in categories:
        score += 20

    for token in tokens:
        if token in title:
            score += 12
        if token in address:
            score += 5

    return score


def _to_result(place: SeoulPlace) -> ChatPlaceResult:
    address = " ".join(part for part in (place.address, place.detail_address) if part)
    return ChatPlaceResult(
        content_id=place.content_id,
        title=place.title,
        category=place.category,
        address=address,
        telephone=place.telephone,
        longitude=place.longitude,
        latitude=place.latitude,
        image_url=place.image_url,
    )


def _answer_for(results: list[ChatPlaceResult]) -> str:
    if not results:
        return (
            "서울 데이터에서 질문과 일치하는 장소를 찾지 못했어요. "
            "지역명이나 관광지, 문화시설, 숙박, 쇼핑, 축제 같은 유형을 함께 입력해 주세요."
        )

    lines = ["서울 공공데이터에서 다음 장소를 찾았어요."]
    for index, result in enumerate(results, start=1):
        location = result.address or "주소 정보 없음"
        lines.append(f"{index}. {result.title} ({result.category}) - {location}")
    return "\n".join(lines)


def answer_region_question(
    message: str,
    max_results: int,
    data_store: SeoulDataStore,
) -> ChatResponse:
    categories = _categories_for(message)
    tokens = _tokens_for(message)

    scored_places = [
        ScoredPlace(place=place, score=score)
        for place in data_store.items
        if (score := _score_place(place, message, tokens, categories)) > 0
    ]
    scored_places.sort(key=lambda item: (-item.score, item.place.title, item.place.content_id))
    results = [_to_result(item.place) for item in scored_places[:max_results]]
    return ChatResponse(answer=_answer_for(results), results=results)
