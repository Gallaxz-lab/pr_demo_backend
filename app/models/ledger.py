import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class AccountType(str, enum.Enum):
    asset = "asset"
    liability = "liability"
    equity = "equity"
    revenue = "revenue"
    expense = "expense"


class Account(Base):
    """Chart of accounts — the backbone of real double-entry bookkeeping. This
    single table + JournalEntry/JournalLine below is what actually separates
    an ERP from a business admin app: every money-moving action posts a
    balanced entry here, so the system can produce a real trial balance
    instead of just dashboard numbers that 'look about right'."""
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(AccountType), nullable=False)


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    memo = Column(String, default="")
    reference = Column(String, default="")  # e.g. "order:1051", "po:12", "settlement:4"
    lines = relationship("JournalLine", back_populates="entry", cascade="all, delete-orphan")


class JournalLine(Base):
    __tablename__ = "journal_lines"
    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit = Column(Float, default=0)
    credit = Column(Float, default=0)
    entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")
