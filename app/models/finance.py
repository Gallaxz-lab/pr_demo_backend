from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class SettlementImport(Base):
    """Phase 3 — one row per marketplace payout line (Shopee/Lazada settlement report)."""
    __tablename__ = "settlement_imports"
    id = Column(Integer, primary_key=True)
    channel = Column(String)
    reference = Column(String)
    gross_amount = Column(Float, default=0)
    fees = Column(Float, default=0)
    net_amount = Column(Float, default=0)
    matched_order_id = Column(Integer, nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class InvoiceRecord(Base):
    """Phase 3 — supplier invoice, OCR'd into a draft accounting entry for review."""
    __tablename__ = "invoice_records"
    id = Column(Integer, primary_key=True)
    vendor = Column(String)
    amount = Column(Float, default=0)
    ocr_raw_text = Column(String, default="")
    status = Column(String, default="draft")  # draft -> reviewed -> posted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
