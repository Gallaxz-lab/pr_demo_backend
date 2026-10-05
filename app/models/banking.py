from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class BankStatementLine(Base):
    """
    FOUNDATION ONLY. Generic (date, description, amount) shape — not matched
    to any real Thai bank's actual export format, since none has been
    provided yet. Matching logic mirrors reconciliation_service.py
    (marketplace settlements) but is even more naive, since bank
    descriptions vary wildly by bank and have no embedded reference format
    assumed here.
    """
    __tablename__ = "bank_statement_lines"
    id = Column(Integer, primary_key=True)
    statement_date = Column(DateTime(timezone=True))
    description = Column(String, default="")
    amount = Column(Float, default=0)
    matched_journal_entry_id = Column(Integer, nullable=True)
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
