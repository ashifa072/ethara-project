from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas import AIQueryRequest, AIQueryResponse
from app.services.ai_service import process_ai_query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/query", response_model=AIQueryResponse)
def ai_query(payload: AIQueryRequest, db: Session = Depends(get_db)):
    answer, intent = process_ai_query(db, payload.query)
    return AIQueryResponse(answer=answer, intent=intent)
