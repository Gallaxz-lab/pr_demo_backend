import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class POStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    received = "received"


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact = Column(String, default="")
    phone = Column(String, default="")


class PurchaseOrder(Base):
    """Procurement — the missing half of 'inventory': how stock actually gets
    replenished, not just how it's deducted on sale. Closes the loop with the
    low-stock forecast (which product) and the general ledger (receiving
    goods posts a real Inventory/Accounts Payable entry, not just a number
    bump)."""
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    status = Column(Enum(POStatus), default=POStatus.draft)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("PurchaseOrderItem", back_populates="po", cascade="all, delete-orphan")
    supplier = relationship("Supplier")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_cost = Column(Float, default=0)
    po = relationship("PurchaseOrder", back_populates="items")
