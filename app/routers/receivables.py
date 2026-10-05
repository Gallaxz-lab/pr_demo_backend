"""Customer invoicing + AR aging — FOUNDATION ONLY, see CustomerInvoice model docstring."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.receivables_service import issue_invoice_for_order, ar_aging
from app.core.security import require_role

router = APIRouter(prefix="/receivables", tags=["receivables — foundation, needs invoice sample + VAT status"])


@router.post("/invoices/from-order/{order_id}", response_model=schemas.CustomerInvoiceOut)
def create_invoice_from_order(order_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return issue_invoice_for_order(db, order)


@router.get("/invoices", response_model=list[schemas.CustomerInvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.CustomerInvoice).all()


@router.post("/invoices/{invoice_id}/mark-paid", response_model=schemas.CustomerInvoiceOut)
def mark_paid(invoice_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    invoice = db.get(models.CustomerInvoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    invoice.status = models.InvoiceStatus.paid
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/ar-aging")
def get_ar_aging(db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    return ar_aging(db)
