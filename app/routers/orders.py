from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/orders", tags=["orders — phase 1"])


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Order)
    if status:
        q = q.filter(models.Order.status == status)
    return q.all()


@router.post("/", response_model=schemas.OrderOut)
def create_order(payload: schemas.OrderCreate, db: Session = Depends(get_db)):
    order = models.Order(customer_id=payload.customer_id, channel=payload.channel)
    db.add(order)
    db.flush()  # get order.id before committing

    total = 0.0
    for item in payload.items:
        product = db.get(models.Product, item.product_id)
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")
        total += product.price * item.quantity
        db.add(models.OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, unit_price=product.price))

    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/verify-payment", response_model=schemas.OrderOut)
def verify_payment(order_id: int, payload: schemas.PaymentVerify, db: Session = Depends(get_db)):
    """Manual payment verification (Phase 1 bullet). On verify: deduct stock and move order to packing."""
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    order.payment_status = models.PaymentStatus.verified if payload.verified else models.PaymentStatus.rejected
    if payload.verified:
        for item in order.items:
            level = db.query(models.StockLevel).filter_by(product_id=item.product_id).first()
            if level:
                level.quantity -= item.quantity
                db.add(models.StockMovement(
                    product_id=item.product_id,
                    change=-item.quantity,
                    reason=f"Order #{order.id} payment verified",
                ))
        order.status = models.OrderStatus.packing

    db.commit()
    db.refresh(order)
    return order
