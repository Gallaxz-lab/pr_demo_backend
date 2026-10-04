"""
Phase 3 — match a marketplace settlement line to an internal order.

Real marketplaces embed an order/reference number in their settlement
export, but the exact format differs per platform (Shopee vs Lazada vs
LINE Shopping) and isn't available without seller-center access. This is
a placeholder matcher — id-in-reference plus amount tolerance — that
makes the reconciliation *workflow* (import -> match -> flag mismatches)
real and testable before the exact per-platform parser is written.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app import models


def match_settlement_to_order(db: Session, reference: str, net_amount: float) -> Optional[models.Order]:
    for order in db.query(models.Order).all():
        if str(order.id) in reference and abs(order.total_amount - net_amount) < max(5.0, order.total_amount * 0.05):
            return order
    return None
