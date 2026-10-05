import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum, Boolean
from app.database import Base


class InvoiceStatus(str, enum.Enum):
    draft = "draft"
    issued = "issued"
    paid = "paid"


class CustomerInvoice(Base):
    """FOUNDATION ONLY. invoice_number format (INV-{year}-{seq:04d}) is a
    placeholder — real Thai tax-invoice (ใบกำกับภาษี) sequential numbering
    rules need confirming against a real sample or an accountant before use.
    Also unconfirmed: whether the shop is even VAT-registered (only
    mandatory above ~฿1.8M annual revenue). Not linked to the general ledger
    yet — pending a decision on whether invoices are always 1:1 with an
    order (already posted to AR at verification) or can stand alone."""
    __tablename__ = "customer_invoices"
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    subtotal = Column(Float, default=0)
    vat_amount = Column(Float, default=0)
    total = Column(Float, default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.draft)
    is_tax_invoice = Column(Boolean, default=False)
