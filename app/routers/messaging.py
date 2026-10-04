"""
Phase 2 — LINE messaging webhook.

Wire in LINE_CHANNEL_SECRET / LINE_CHANNEL_ACCESS_TOKEN in .env once you
have a real LINE Official Account; until then this runs in dev mode (see
line_service.py) so the routing logic — incoming text -> catalog-grounded
AI Q&A -> reply — is already testable with curl/Postman.
"""
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_service import answer_product_question
from app.services.line_service import verify_signature, reply_message

router = APIRouter(prefix="/messaging", tags=["messaging — phase 2"])


@router.post("/line/webhook")
async def line_webhook(request: Request, x_line_signature: Optional[str] = Header(None), db: Session = Depends(get_db)):
    body = await request.body()
    if not verify_signature(body, x_line_signature):
        raise HTTPException(400, "Invalid signature")

    payload = await request.json()
    for event in payload.get("events", []):
        if event.get("type") == "message" and event.get("message", {}).get("type") == "text":
            question = event["message"]["text"]
            reply_token = event["replyToken"]
            answer = answer_product_question(question, db)
            reply_message(reply_token, answer["answer"])
    return {"status": "ok"}
