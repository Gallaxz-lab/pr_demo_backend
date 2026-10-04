from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/catalog", tags=["catalog — phase 1"])


@router.get("/products", response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.post("/products", response_model=schemas.ProductOut)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    if db.query(models.Product).filter_by(sku=payload.sku).first():
        raise HTTPException(400, "SKU already exists")
    product = models.Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    db.add(models.StockLevel(product_id=product.id, quantity=0))
    db.commit()
    return product


@router.get("/compatibility")
def check_compatibility(bike_model: str, sku: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter_by(sku=sku).first()
    if not product:
        raise HTTPException(404, "Unknown SKU")
    matches = [c for c in product.compatibility if bike_model.lower() in c.bike_model.lower()]
    return {"fits": bool(matches), "matches": [schemas.CompatibilityOut.model_validate(m) for m in matches]}
