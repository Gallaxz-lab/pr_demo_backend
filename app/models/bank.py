from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class BankStatementLine(Base):
    """FOUNDATION ONLY — column shape (date, description, amount) is a guess.
    Every Thai bank exports differently; this hasn't been built against a
    real sample statement, same caveat as marketplace settlement matching."""
    __tablename__ = "bank_statement_lines"
    id = Column(Integer, primary_key=True)
    bank_name = Column(String, default="")
    statement_date = Column(DateTime(timezone=True))
    description = Column(String, default="")
    amount = Column(Float, default=0)
    matched = Column(String, default="unmatched")
    imported_at = Column(DateTime(timezone=True), server_default=func.now())
