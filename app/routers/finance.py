"""
Phase 3 — marketplace settlement reconciliation and invoice OCR drafts.

Invoice OCR is a real implementation (Claude vision API, see ocr_service.py)
once ANTHROPIC_API_KEY is set. Settlement matching is real matching logic,
but against a placeholder reference format — real Shopee/Lazada exports
need seller-center access to see their actual format, which this build
doesn't have.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.reconciliation_service import match_settlement_to_order
from app.services.ocr_service import extract_invoice_fields

router = APIRouter(prefix="/finance", tags=["finance — phase 3"])


@router.post("/settlements/import")
def import_settlement(payload: schemas.SettlementImportCreate, db: Session = Depends(get_db)):
    net = payload.gross_amount - payload.fees
    match = match_settlement_to_order(db, payload.reference, net)
    record = models.SettlementImport(
        channel=payload.channel,
        reference=payload.reference,
        gross_amount=payload.gross_amount,
        fees=payload.fees,
        net_amount=net,
        matched_order_id=match.id if match else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/invoices/ocr")
def ocr_invoice(payload: schemas.InvoiceOcrRequest, db: Session = Depends(get_db)):
    fields = extract_invoice_fields(payload.image_base64, payload.media_type)
    record = models.InvoiceRecord(
        vendor=fields.get("vendor", "unknown"),
        amount=fields.get("amount", 0),
        ocr_raw_text=fields.get("raw_text", ""),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
