"""
Phase 1 — catalog-grounded product Q&A.

Design principle: never let the model answer from open knowledge. Retrieve
matching catalog + compatibility + stock rows first, pass ONLY those rows to
the model as context, and instruct it to say "not sure, admin will confirm"
rather than guess. This is what makes auto-sent replies trustworthy instead
of a hallucination risk.

Works with no ANTHROPIC_API_KEY set (deterministic fallback below), so the
Phase 1 demo runs without any external credentials.
"""
import os
import re
import httpx
from sqlalchemy.orm import Session
from app import models

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def _find_candidate_products(question: str, db: Session):
    words = re.findall(r"[\w\u0E00-\u0E7F]+", question.lower())
    products = db.query(models.Product).all()
    scored = []
    for p in products:
        haystack = f"{p.name} {p.sku} {' '.join(c.bike_model for c in p.compatibility)}".lower()
        score = sum(1 for w in words if len(w) > 2 and w in haystack)
        if score:
            scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    return [p for _, p in scored[:3]]


def _catalog_context(db: Session, products) -> str:
    lines = []
    for p in products:
        level = db.query(models.StockLevel).filter_by(product_id=p.id).first()
        qty = level.quantity if level else "unknown"
        compat = "; ".join(f"{c.bike_make} {c.bike_model} ({c.year_from}-{c.year_to})" for c in p.compatibility) or "no listed models"
        lines.append(f"SKU {p.sku} — {p.name} — ฿{p.price} — stock: {qty} — compatible: {compat}")
    return "\n".join(lines) if lines else "No matching catalog records found."


def _stock_for(db: Session, product) -> int | None:
    level = db.query(models.StockLevel).filter_by(product_id=product.id).first()
    return level.quantity if level else None


def answer_product_question(question: str, db: Session) -> dict:
    candidates = _find_candidate_products(question, db)
    context = _catalog_context(db, candidates)
    grounded_sku = candidates[0].sku if candidates else None
    stock_now = _stock_for(db, candidates[0]) if candidates else None

    if not ANTHROPIC_API_KEY:
        if candidates:
            p = candidates[0]
            return {
                "answer": f"Based on our catalog — {p.name} (SKU {p.sku}): {context}",
                "grounded_sku": grounded_sku,
                "stock_at_answer_time": stock_now,
            }
        return {
            "answer": "I couldn't find a matching catalog record for that. An admin will check and reply.",
            "grounded_sku": None,
            "stock_at_answer_time": None,
        }

    system_prompt = (
        "You are a parts-fitment assistant for a Thai motorcycle performance shop. "
        "Answer ONLY using the catalog records below. If they don't clearly answer "
        "the question, say you're not sure and that an admin will confirm — never "
        "guess compatibility. Reply in the same language as the question, briefly.\n\n"
        f"Catalog records:\n{context}"
    )
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [{"role": "user", "content": question}],
        },
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    return {"answer": text.strip(), "grounded_sku": grounded_sku, "stock_at_answer_time": stock_now}
