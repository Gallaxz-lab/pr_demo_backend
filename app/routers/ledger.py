"""General ledger — read side. Posting happens from orders/finance/procurement
routers via ledger_service.post_journal_entry(), never directly here."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.ledger_service import trial_balance
from app.core.security import require_role

router = APIRouter(prefix="/ledger", tags=["general ledger — erp core"])


@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    return [{"id": a.id, "code": a.code, "name": a.name, "type": a.type.value} for a in db.query(models.Account).all()]


@router.get("/trial-balance")
def get_trial_balance(db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    return trial_balance(db)


@router.get("/entries")
def list_entries(db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    entries = db.query(models.JournalEntry).order_by(models.JournalEntry.id.desc()).limit(100).all()
    return [
        {
            "id": e.id, "date": e.date, "memo": e.memo, "reference": e.reference,
            "lines": [{"account": l.account.code, "debit": l.debit, "credit": l.credit} for l in e.lines],
        }
        for e in entries
    ]
