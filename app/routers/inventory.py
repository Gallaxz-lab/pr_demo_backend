from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.audit_service import log_action
from app.core.security import require_role

router = APIRouter(prefix="/inventory", tags=["inventory — phase 1"])


@router.get("/stock")
def list_stock(low_only: bool = False, db: Session = Depends(get_db)):
    levels = db.query(models.StockLevel).all()
    if low_only:
        levels = [l for l in levels if l.quantity <= l.reorder_threshold]
    return [{"product_id": l.product_id, "quantity": l.quantity, "reorder_threshold": l.reorder_threshold} for l in levels]


@router.post("/movements", response_model=schemas.StockMovementOut)
def record_movement(payload: schemas.StockMovementCreate, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin", "staff"))):
    level = db.query(models.StockLevel).filter_by(product_id=payload.product_id).first()
    if not level:
        raise HTTPException(404, "No stock record for this product")
    level.quantity += payload.change
    movement = models.StockMovement(**payload.model_dump())
    db.add(movement)
    db.commit()
    db.refresh(movement)
    log_action(db, actor=user.username, action="inventory.movement", entity="product", entity_id=payload.product_id, detail=f"{payload.change:+d} ({payload.reason})")
    return movement
