"""Approval workflow — FOUNDATION ONLY, threshold is a placeholder pending owner sign-off."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.core.security import require_role

router = APIRouter(prefix="/approvals", tags=["approvals — foundation, threshold needs owner sign-off"])


@router.get("/", response_model=list[schemas.ApprovalOut])
def list_approvals(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Approval)
    if status:
        q = q.filter(models.Approval.status == status)
    return q.all()


@router.post("/{approval_id}/approve", response_model=schemas.ApprovalOut)
def approve(approval_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner"))):
    approval = db.get(models.Approval, approval_id)
    if not approval:
        raise HTTPException(404, "Approval not found")
    approval.status = models.ApprovalStatus.approved
    approval.approved_by = user.username
    db.commit()
    db.refresh(approval)
    return approval


@router.post("/{approval_id}/reject", response_model=schemas.ApprovalOut)
def reject(approval_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner"))):
    approval = db.get(models.Approval, approval_id)
    if not approval:
        raise HTTPException(404, "Approval not found")
    approval.status = models.ApprovalStatus.rejected
    approval.approved_by = user.username
    db.commit()
    db.refresh(approval)
    return approval
