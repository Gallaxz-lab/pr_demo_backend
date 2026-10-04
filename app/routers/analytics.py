"""Phase 3 — sales analytics and low-stock forecasting."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models

router = APIRouter(prefix="/analytics", tags=["analytics — phase 3"])


@router.get("/low-stock-forecast")
def low_stock_forecast(db: Session = Depends(get_db)):
    """
    Currently a threshold flag, not a real forecast: anything at/under its
    reorder_threshold. stock_movements already records every change with a
    timestamp, so a velocity-based forecast (units/week -> days until
    stockout) can be built on top of this without a schema change.
    """
    levels = db.query(models.StockLevel).all()
    return [
        {"product_id": l.product_id, "quantity": l.quantity, "reorder_threshold": l.reorder_threshold}
        for l in levels if l.quantity <= l.reorder_threshold
    ]


@router.get("/sales-summary")
def sales_summary(db: Session = Depends(get_db)):
    total = (
        db.query(func.sum(models.Order.total_amount))
        .filter(models.Order.payment_status == models.PaymentStatus.verified)
        .scalar() or 0
    )
    by_channel = (
        db.query(models.Order.channel, func.sum(models.Order.total_amount))
        .filter(models.Order.payment_status == models.PaymentStatus.verified)
        .group_by(models.Order.channel)
        .all()
    )
    return {"total_verified_revenue": total, "by_channel": {c: amt for c, amt in by_channel}}
