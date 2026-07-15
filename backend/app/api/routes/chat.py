from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import (
    answer_post_question,
    answer_region_question,
    is_post_search_question,
)
from app.services.seoul_data import seoul_data_store

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, database: Session = Depends(get_db)) -> ChatResponse:
    if is_post_search_question(request.message):
        return answer_post_question(
            message=request.message,
            max_results=request.max_results,
            database=database,
        )

    if not seoul_data_store.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="서울 지역 데이터가 준비되지 않았습니다.",
        )

    return answer_region_question(
        message=request.message,
        max_results=request.max_results,
        data_store=seoul_data_store,
    )
