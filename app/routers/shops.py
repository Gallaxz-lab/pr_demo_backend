"""
Multi-tenancy — FOUNDATION ONLY. See Shop model docstring: this proves the
pattern (a Shop table + AdminUser.shop_id) but nothing else in the app is
actually scoped by shop yet. Turning this into real multi-tenancy is a
deliberate, larger decision (sell to one shop vs many) — not something to
half-build silently.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/shops", tags=["shops — multi-tenancy foundation only, not enforced"])


@router.get("/", response_model=list[schemas.ShopOut])
def list_shops(db: Session = Depends(get_db)):
    return db.query(models.Shop).all()


@router.post("/", response_model=schemas.ShopOut)
def create_shop(payload: schemas.ShopCreate, db: Session = Depends(get_db)):
    shop = models.Shop(**payload.model_dump())
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop
