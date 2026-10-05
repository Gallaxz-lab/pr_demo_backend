"""
FOUNDATION ONLY — mirrors the same placeholder-matching approach as
reconciliation_service.py (marketplace settlements), but against a generic
statement-line shape. No real Thai bank export format has been provided to
build real parsing against; send a sample CSV/Excel export from the shop's
actual bank to replace this with real matching logic.
"""
from sqlalchemy.orm import Session
from app import models


def match_statement_line(db: Session, description: str, amount: float):
    """Looks for a Cash-account journal line with a close-enough amount.
    Extremely naive — ignores dates, ignores running balance, and doesn't
    use any reference number a real bank export would actually contain."""
    cash_account = db.query(models.Account).filter_by(code="1000").first()
    if not cash_account:
        return None
    for line in db.query(models.JournalLine).filter_by(account_id=cash_account.id).all():
        if abs(line.debit - amount) < 1.0 or abs(line.credit - amount) < 1.0:
            return line.entry_id
    return None
