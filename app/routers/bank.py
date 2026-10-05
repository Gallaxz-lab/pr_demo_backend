from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.bank_reconciliation_service import match_statement_line
from app.core.security import require_role

router = APIRouter(prefix="/bank", tags=["bank reconciliation — foundation, needs real statement sample"])


@router.post("/statement/import")
def import_statement_lines(payload: list[schemas.BankStatementLineCreate], db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    results = []
    for item in payload:
        line = models.BankStatementLine(bank_name=item.bank_name, statement_date=item.statement_date, description=item.description, amount=item.amount)
        db.add(line)
        db.commit()
        db.refresh(line)
        match = match_statement_line(db, line)
        line.matched = "matched" if match else "unmatched"
        db.commit()
        results.append({"id": line.id, "description": line.description, "amount": line.amount, "matched": line.matched})
    return results


@router.get("/statement")
def list_statement_lines(db: Session = Depends(get_db)):
    return [{"id": l.id, "bank_name": l.bank_name, "description": l.description, "amount": l.amount, "matched": l.matched} for l in db.query(models.BankStatementLine).all()]
