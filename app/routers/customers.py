from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/customers", tags=["customers — phase 1"])


@router.get("/", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()


@router.post("/", response_model=schemas.CustomerOut)
def create_customer(payload: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = models.Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}/history")
def customer_history(customer_id: int, db: Session = Depends(get_db)):
    """Phase 2 bullet ('customer and service history') — order + repair-job history in one place."""
    customer = db.get(models.Customer, customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    return {
        "customer": customer.name,
        "orders": [o.id for o in customer.orders],
        "repair_jobs": [j.id for j in customer.repair_jobs],
    }
