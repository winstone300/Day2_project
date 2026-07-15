import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.schemas.chat import ChatPlaceResult, ChatPostResult, ChatResponse
from app.services.post_service import get_posts
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

POST_INTENT_KEYWORDS = (
    "게시글",
    "게시판",
    "커뮤니티",
    "작성한 글",
    "올라온 글",
)

POST_QUERY_STOP_WORDS = (
    *POST_INTENT_KEYWORDS,
    "검색해줘",
    "검색해주세요",
    "검색",
    "찾아줘",
    "찾아주세요",
    "찾아",
    "보여줘",
    "보여주세요",
    "최근",
    "관련된",
    "관련",
    "에서",
    "글",
)


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


def is_post_search_question(message: str) -> bool:
    normalized_message = _normalized(message)
    return any(_normalized(keyword) in normalized_message for keyword in POST_INTENT_KEYWORDS)


def _post_query_for(message: str) -> str:
    query = message.lower()
    for stop_word in sorted(POST_QUERY_STOP_WORDS, key=len, reverse=True):
        query = query.replace(stop_word, " ")
    return " ".join(TOKEN_PATTERN.findall(query)).strip()


def _post_preview(content: str, limit: int = 120) -> str:
    preview = " ".join(content.split())
    return preview if len(preview) <= limit else f"{preview[:limit].rstrip()}…"


def answer_post_question(message: str, max_results: int, database: Session) -> ChatResponse:
    query = _post_query_for(message)
    posts, _ = get_posts(
        database,
        page=1,
        size=max_results,
        query=query or None,
        sort="latest",
    )
    results = [
        ChatPostResult(
            id=post.id,
            title=post.title,
            content_preview=_post_preview(post.content),
            view_count=post.view_count,
            created_at=post.created_at,
        )
        for post in posts
    ]

    if not results:
        answer = f"커뮤니티에서 ‘{query}’와 관련된 게시글을 찾지 못했어요."
    elif query:
        answer = f"커뮤니티에서 ‘{query}’와 관련된 게시글 {len(results)}건을 찾았어요."
    else:
        answer = f"커뮤니티의 최근 게시글 {len(results)}건을 가져왔어요."

    return ChatResponse(
        answer=answer,
        intent="post_search",
        post_results=results,
        source="LocalHub 서울 커뮤니티",
    )
