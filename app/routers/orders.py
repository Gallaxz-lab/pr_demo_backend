from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.ledger_service import post_journal_entry
from app.services.audit_service import log_action
from app.core.security import require_role

router = APIRouter(prefix="/orders", tags=["orders — phase 1"])

MARKETPLACE_CHANNELS = {"shopee", "lazada"}


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
    db.flush()

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
def verify_payment(order_id: int, payload: schemas.PaymentVerify, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin", "staff"))):
    """Manual payment verification. On verify: deduct stock, log the movement,
    and post real GL entries — Cash for LINE/manual orders (an admin just
    confirmed a payment slip), Accounts Receivable for marketplace orders
    (the platform owes you, cleared later by a matching settlement import)."""
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    if not payload.verified:
        order.payment_status = models.PaymentStatus.rejected
        db.commit()
        log_action(db, actor=user.username, action="order.reject_payment", entity="order", entity_id=order.id)
        db.refresh(order)
        return order

    order.payment_status = models.PaymentStatus.verified
    total_cost = 0.0
    for item in order.items:
        level = db.query(models.StockLevel).filter_by(product_id=item.product_id).first()
        if level:
            level.quantity -= item.quantity
            db.add(models.StockMovement(product_id=item.product_id, change=-item.quantity, reason=f"Order #{order.id} payment verified"))
        product = db.get(models.Product, item.product_id)
        if product:
            total_cost += (product.cost_price or 0) * item.quantity
    order.status = models.OrderStatus.packing
    db.commit()

    cash_or_ar = "1100" if order.channel in MARKETPLACE_CHANNELS else "1000"
    post_journal_entry(
        db, memo=f"Sale — order #{order.id}", reference=f"order:{order.id}",
        lines=[(cash_or_ar, order.total_amount, 0), ("4000", 0, order.total_amount)],
    )
    if total_cost > 0:
        post_journal_entry(
            db, memo=f"COGS — order #{order.id}", reference=f"order:{order.id}",
            lines=[("5000", total_cost, 0), ("1200", 0, total_cost)],
        )
    log_action(db, actor=user.username, action="order.verify_payment", entity="order", entity_id=order.id, detail=f"verified, total=฿{order.total_amount}")

    db.refresh(order)
    return order
