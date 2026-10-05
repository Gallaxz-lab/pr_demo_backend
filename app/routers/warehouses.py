"""
Multi-warehouse — FOUNDATION ONLY. One 'Main Warehouse' is seeded and used
implicitly everywhere else (orders, PO receiving, manual stock movements
default to it). These are the only endpoints that actually expose warehouse
choice; nothing else in the app lets you pick a location per-transaction.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.audit_service import log_action
from app.core.security import require_role

router = APIRouter(prefix="/warehouses", tags=["warehouses — foundation, not yet wired everywhere"])


@router.get("/")
def list_warehouses(db: Session = Depends(get_db)):
    return [{"id": w.id, "name": w.name, "address": w.address, "is_default": w.is_default} for w in db.query(models.Warehouse).all()]


@router.post("/")
def create_warehouse(payload: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    wh = models.Warehouse(**payload.model_dump())
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh


@router.get("/stock")
def stock_by_warehouse(product_id: int, db: Session = Depends(get_db)):
    levels = db.query(models.StockLevel).filter_by(product_id=product_id).all()
    return [{"warehouse_id": l.warehouse_id, "quantity": l.quantity} for l in levels]


@router.post("/transfer", response_model=schemas.StockTransferOut)
def transfer_stock(payload: schemas.StockTransferCreate, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin", "staff"))):
    source = db.query(models.StockLevel).filter_by(product_id=payload.product_id, warehouse_id=payload.from_warehouse_id).first()
    if not source or source.quantity < payload.quantity:
        raise HTTPException(400, "Not enough stock at source warehouse")
    dest = db.query(models.StockLevel).filter_by(product_id=payload.product_id, warehouse_id=payload.to_warehouse_id).first()
    if not dest:
        dest = models.StockLevel(product_id=payload.product_id, warehouse_id=payload.to_warehouse_id, quantity=0, reorder_threshold=source.reorder_threshold)
        db.add(dest)
        db.flush()

    source.quantity -= payload.quantity
    dest.quantity += payload.quantity
    db.add(models.StockMovement(product_id=payload.product_id, warehouse_id=payload.from_warehouse_id, change=-payload.quantity, reason=f"Transfer to warehouse {payload.to_warehouse_id}"))
    db.add(models.StockMovement(product_id=payload.product_id, warehouse_id=payload.to_warehouse_id, change=payload.quantity, reason=f"Transfer from warehouse {payload.from_warehouse_id}"))
    db.commit()
    log_action(db, actor=user.username, action="warehouse.transfer", entity="product", entity_id=payload.product_id, detail=f"{payload.quantity} units {payload.from_warehouse_id}->{payload.to_warehouse_id}")
    return {"product_id": payload.product_id, "from_warehouse_id": payload.from_warehouse_id, "to_warehouse_id": payload.to_warehouse_id, "quantity": payload.quantity, "source_remaining": source.quantity, "dest_total": dest.quantity}
