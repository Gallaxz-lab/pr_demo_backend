"""
FOUNDATION ONLY — APPROVAL_THRESHOLD is a placeholder (฿10,000) pending a
real policy decision from the shop owner: what should require approval,
above what amount, and approved by whom. Currently wired into purchase
orders only (see procurement.py) — nothing else checks this yet.
"""
from sqlalchemy.orm import Session
from app import models

APPROVAL_THRESHOLD = 10000  # PLACEHOLDER — confirm with the shop owner


def requires_approval(amount: float) -> bool:
    return amount >= APPROVAL_THRESHOLD


def create_approval_request(db: Session, entity_type: str, entity_id: int, amount: float, requested_by: str) -> models.Approval:
    approval = models.Approval(entity_type=entity_type, entity_id=entity_id, amount=amount, requested_by=requested_by)
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def is_approved(db: Session, entity_type: str, entity_id: int) -> bool:
    approval = db.query(models.Approval).filter_by(entity_type=entity_type, entity_id=entity_id).order_by(models.Approval.id.desc()).first()
    return approval is not None and approval.status == models.ApprovalStatus.approved
