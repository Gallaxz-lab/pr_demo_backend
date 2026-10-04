from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas
from app.services.ai_service import answer_product_question

router = APIRouter(prefix="/ai", tags=["ai product q&a — phase 1"])


@router.post("/qa", response_model=schemas.QAResponse)
def ask(payload: schemas.QARequest, db: Session = Depends(get_db)):
    """Catalog-grounded Q&A — same logic the LINE webhook (Phase 2) calls into."""
    return answer_product_question(payload.question, db)
