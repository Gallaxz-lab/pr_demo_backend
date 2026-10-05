from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.ledger_service import post_journal_entry
from app.services.audit_service import log_action
from app.services.approval_service import requires_approval, create_approval_request, is_approved, APPROVAL_THRESHOLD
from app.core.security import require_role

router = APIRouter(prefix="/procurement", tags=["procurement — erp core"])


@router.get("/suppliers", response_model=list[schemas.SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(models.Supplier).all()


@router.post("/suppliers", response_model=schemas.SupplierOut)
def create_supplier(payload: schemas.SupplierCreate, db: Session = Depends(get_db)):
    supplier = models.Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/purchase-orders", response_model=list[schemas.PurchaseOrderOut])
def list_pos(db: Session = Depends(get_db)):
    return db.query(models.PurchaseOrder).all()


@router.post("/purchase-orders", response_model=schemas.PurchaseOrderOut)
def create_po(payload: schemas.PurchaseOrderCreate, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin", "staff"))):
    po = models.PurchaseOrder(supplier_id=payload.supplier_id)
    db.add(po)
    db.flush()
    total = 0.0
    for item in payload.items:
        db.add(models.PurchaseOrderItem(po_id=po.id, product_id=item.product_id, quantity=item.quantity, unit_cost=item.unit_cost))
        total += item.unit_cost * item.quantity
    db.commit()
    db.refresh(po)

    # Foundation-only approval gate — see approval_service.py for the placeholder threshold.
    if requires_approval(total):
        create_approval_request(db, entity_type="purchase_order", entity_id=po.id, amount=total, requested_by=user.username)
    return po


@router.post("/purchase-orders/{po_id}/receive", response_model=schemas.PurchaseOrderOut)
def receive_po(po_id: int, db: Session = Depends(get_db), user=Depends(require_role("owner", "admin", "staff"))):
    """Marks goods received: increases stock, logs movements, and posts a real
    GL entry (Debit Inventory, Credit Accounts Payable). Blocked if the PO's
    total is at/above the placeholder approval threshold and hasn't been
    approved yet — see approval_service.py."""
    po = db.get(models.PurchaseOrder, po_id)
    if not po:
        raise HTTPException(404, "Purchase order not found")
    if po.status == models.POStatus.received:
        raise HTTPException(400, "Already received")

    total_cost = sum(item.unit_cost * item.quantity for item in po.items)
    if requires_approval(total_cost) and not is_approved(db, "purchase_order", po.id):
        raise HTTPException(403, f"PO total ฿{total_cost} is at/above the ฿{APPROVAL_THRESHOLD} approval threshold and hasn't been approved yet — see POST /approvals/{{id}}/approve")

    for item in po.items:
        level = db.query(models.StockLevel).filter_by(product_id=item.product_id).first()
        if level:
            level.quantity += item.quantity
        db.add(models.StockMovement(product_id=item.product_id, change=item.quantity, reason=f"PO #{po.id} received"))

    po.status = models.POStatus.received
    db.commit()

    if total_cost > 0:
        post_journal_entry(
            db, memo=f"Goods received — PO #{po.id}", reference=f"po:{po.id}",
            lines=[("1200", total_cost, 0), ("2000", 0, total_cost)],
        )
    log_action(db, actor=user.username, action="po.receive", entity="purchase_order", entity_id=po.id, detail=f"฿{total_cost}")
    db.refresh(po)
    return po
