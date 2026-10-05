import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from app.database import Base


class InvoiceStatus(str, enum.Enum):
    unpaid = "unpaid"
    paid = "paid"


class CustomerInvoice(Base):
    """
    Customer-facing AR invoice — FOUNDATION ONLY. invoice_number below uses
    a placeholder sequential format, NOT verified against Thai Revenue
    Department sequential-numbering rules for tax invoices (ใบกำกับภาษี).
    VAT is assumed at a flat 7% with no TIN/VAT-registration check. Do not
    issue these as real tax invoices until: (1) the shop's VAT-registration
    status is confirmed, (2) a real invoice sample or their accountant's
    format spec is provided.
    """
    __tablename__ = "customer_invoices"
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    subtotal = Column(Float, default=0)
    vat_amount = Column(Float, default=0)
    total_amount = Column(Float, default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.unpaid)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
