"""
DEMO ESTIMATOR ONLY — see payroll_service.py docstring. SSF uses a
placeholder rate/cap; withholding tax is left at 0 rather than guessed.
Do not use for real payroll without accountant review.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.payroll_service import estimate_payslip
from app.core.security import require_role

router = APIRouter(prefix="/payroll", tags=["payroll — DEMO ESTIMATOR ONLY, not for real use"])


@router.get("/employees", response_model=list[schemas.EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()


@router.post("/employees", response_model=schemas.EmployeeOut)
def create_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    emp = models.Employee(**payload.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.post("/run", response_model=schemas.PayslipOut)
def run_payroll_for_employee(employee_id: int, period: str, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin"))):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    calc = estimate_payslip(emp.monthly_salary)
    slip = models.Payslip(employee_id=emp.id, period=period, **calc)
    db.add(slip)
    db.commit()
    db.refresh(slip)
    return slip


@router.get("/payslips", response_model=list[schemas.PayslipOut])
def list_payslips(db: Session = Depends(get_db)):
    return db.query(models.Payslip).all()
