"""
FOUNDATION ONLY. next_invoice_number() uses a placeholder format, not a
Revenue-Department-verified sequence. VAT_RATE assumes the shop is VAT
registered at the standard 7% rate with no TIN check — confirm actual
registration status before using this for real tax invoices.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models

VAT_RATE = 0.07  # placeholder — confirm the shop's actual VAT-registration status


def next_invoice_number(db: Session) -> str:
    # Placeholder format: INV-<Buddhist Era year>-<sequence>. Real Revenue
    # Department sequential-numbering rules have NOT been verified here.
    year_be = datetime.utcnow().year + 543
    count = db.query(models.CustomerInvoice).count() + 1
    return f"INV-{year_be}-{count:04d}"


def issue_invoice_for_order(db: Session, order: models.Order, due_days: int = 30) -> models.CustomerInvoice:
    subtotal = round(order.total_amount / (1 + VAT_RATE), 2)
    vat = round(order.total_amount - subtotal, 2)
    invoice = models.CustomerInvoice(
        invoice_number=next_invoice_number(db),
        order_id=order.id,
        customer_id=order.customer_id,
        subtotal=subtotal,
        vat_amount=vat,
        total_amount=order.total_amount,
        due_date=datetime.utcnow() + timedelta(days=due_days),
    )
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def ar_aging(db: Session) -> dict:
    now = datetime.utcnow()
    buckets = {"current": [], "1-30": [], "31-60": [], "61-90": [], "90+": []}
    for inv in db.query(models.CustomerInvoice).filter_by(status=models.InvoiceStatus.unpaid).all():
        days_overdue = (now - inv.due_date.replace(tzinfo=None)).days if inv.due_date else 0
        if days_overdue <= 0: bucket = "current"
        elif days_overdue <= 30: bucket = "1-30"
        elif days_overdue <= 60: bucket = "31-60"
        elif days_overdue <= 90: bucket = "61-90"
        else: bucket = "90+"
        buckets[bucket].append({"invoice_number": inv.invoice_number, "customer_id": inv.customer_id, "amount": inv.total_amount, "days_overdue": max(days_overdue, 0)})
    return buckets
