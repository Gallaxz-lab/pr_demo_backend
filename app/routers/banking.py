"""Bank reconciliation — FOUNDATION ONLY, see bank_reconciliation_service.py."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.bank_reconciliation_service import match_statement_line
from app.core.security import require_role

router = APIRouter(prefix="/banking", tags=["banking — foundation, needs a real bank export sample"])


@router.post("/statement-lines/import", response_model=schemas.BankStatementLineOut)
def import_statement_line(payload: schemas.BankStatementLineCreate, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    matched = match_statement_line(db, payload.description, payload.amount)
    line = models.BankStatementLine(
        statement_date=payload.statement_date, description=payload.description,
        amount=payload.amount, matched_journal_entry_id=matched,
    )
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@router.get("/statement-lines", response_model=list[schemas.BankStatementLineOut])
def list_statement_lines(db: Session = Depends(get_db)):
    return db.query(models.BankStatementLine).all()
