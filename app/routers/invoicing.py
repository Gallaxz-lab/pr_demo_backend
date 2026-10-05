"""
Customer-facing invoicing + AR aging — FOUNDATION ONLY.

Two things are explicitly unconfirmed before this touches a real customer:
  1. invoice_number format (placeholder: INV-{year}-{seq:04d}) — real Thai
     tax-invoice sequential numbering rules need a sample invoice or
     accountant confirmation.
  2. Whether the shop is VAT-registered at all (mandatory tax invoices
     generally only apply above ~฿1.8M annual revenue).
PDF generation is intentionally not implemented — layout depends on both
of the above being settled first.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/invoices", tags=["customer invoicing — foundation, needs confirmation"])


def _next_invoice_number(db: Session) -> str:
    year = datetime.utcnow().year
    count = db.query(models.CustomerInvoice).count() + 1
    return f"INV-{year}-{count:04d}"  # PLACEHOLDER FORMAT


@router.post("/", response_model=schemas.CustomerInvoiceOut)
def create_invoice(payload: schemas.CustomerInvoiceCreate, db: Session = Depends(get_db)):
    invoice = models.CustomerInvoice(
        invoice_number=_next_invoice_number(db),
        customer_id=payload.customer_id,
        order_id=payload.order_id,
        due_date=datetime.utcnow() + timedelta(days=payload.due_in_days),
        subtotal=payload.subtotal,
        vat_amount=payload.vat_amount,
        total=payload.subtotal + payload.vat_amount,
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/", response_model=list[schemas.CustomerInvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.CustomerInvoice).all()


@router.post("/{invoice_id}/mark-paid", response_model=schemas.CustomerInvoiceOut)
def mark_paid(invoice_id: int, db: Session = Depends(get_db)):
    inv = db.get(models.CustomerInvoice, invoice_id)
    if not inv:
        raise HTTPException(404, "Invoice not found")
    inv.status = models.InvoiceStatus.paid
    db.commit()
    db.refresh(inv)
    return inv


@router.get("/aging")
def ar_aging(db: Session = Depends(get_db)):
    """0-30 / 31-60 / 61-90 / 90+ days overdue, by unpaid invoice total."""
    now = datetime.utcnow()
    buckets = {"0-30": 0.0, "31-60": 0.0, "61-90": 0.0, "90+": 0.0}
    for inv in db.query(models.CustomerInvoice).filter(models.CustomerInvoice.status != models.InvoiceStatus.paid).all():
        if not inv.due_date:
            continue
        days_overdue = (now - inv.due_date.replace(tzinfo=None)).days
        bucket = "0-30" if days_overdue <= 30 else "31-60" if days_overdue <= 60 else "61-90" if days_overdue <= 90 else "90+"
        buckets[bucket] += inv.total
    return buckets
