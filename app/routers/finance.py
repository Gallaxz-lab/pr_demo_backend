"""
Phase 3 — marketplace settlement reconciliation and invoice OCR, now posting
real journal entries instead of just updating status fields.

Invoice OCR is a real implementation (Claude vision API, see ocr_service.py)
once ANTHROPIC_API_KEY is set. Settlement matching is real matching logic,
but against a placeholder reference format — real Shopee/Lazada exports
need seller-center access to see their actual format, which this build
doesn't have.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.reconciliation_service import match_settlement_to_order
from app.services.ocr_service import extract_invoice_fields
from app.services.ledger_service import post_journal_entry
from app.services.audit_service import log_action
from app.core.security import require_role

router = APIRouter(prefix="/finance", tags=["finance — phase 3"])


@router.get("/settlements", response_model=list[schemas.SettlementImportOut])
def list_settlements(db: Session = Depends(get_db)):
    return db.query(models.SettlementImport).all()


@router.post("/settlements/import", response_model=schemas.SettlementImportOut)
def import_settlement(payload: schemas.SettlementImportCreate, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    net = payload.gross_amount - payload.fees
    match = match_settlement_to_order(db, payload.reference, net)
    record = models.SettlementImport(
        channel=payload.channel, reference=payload.reference,
        gross_amount=payload.gross_amount, fees=payload.fees, net_amount=net,
        matched_order_id=match.id if match else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if match:
        # Clears the Accounts Receivable created when the marketplace order
        # was verified: cash in, fees expensed, AR cleared by the gross amount.
        post_journal_entry(
            db, memo=f"Settlement — {payload.channel} {payload.reference}", reference=f"settlement:{record.id}",
            lines=[("1000", net, 0), ("5100", payload.fees, 0), ("1100", 0, payload.gross_amount)],
        )
    log_action(db, actor=user.username, action="finance.settlement_import", entity="settlement", entity_id=record.id, detail=f"matched_order={match.id if match else None}")
    return record


@router.get("/invoices", response_model=list[schemas.InvoiceRecordOut])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.InvoiceRecord).all()


@router.post("/invoices/ocr", response_model=schemas.InvoiceRecordOut)
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


@router.post("/invoices/{invoice_id}/post", response_model=schemas.InvoiceRecordOut)
def post_invoice(invoice_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    """Moves a draft OCR'd invoice into the books: Debit Expense, Credit
    Accounts Payable. This is the human-review gate — OCR output never
    reaches the ledger without this explicit step."""
    invoice = db.get(models.InvoiceRecord, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    if invoice.status == "posted":
        raise HTTPException(400, "Already posted")

    post_journal_entry(
        db, memo=f"Supplier invoice — {invoice.vendor}", reference=f"invoice:{invoice.id}",
        lines=[("5200", invoice.amount, 0), ("2000", 0, invoice.amount)],
    )
    invoice.status = "posted"
    db.commit()
    log_action(db, actor=user.username, action="finance.invoice_post", entity="invoice", entity_id=invoice.id, detail=f"฿{invoice.amount}")
    db.refresh(invoice)
    return invoice
