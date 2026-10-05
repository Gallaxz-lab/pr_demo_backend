from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Warehouse(Base):
    """Multi-warehouse — FOUNDATION ONLY. One 'Main Warehouse' is seeded
    automatically and everything else in the app (orders, PO receiving,
    plain stock movements) implicitly uses it. Only /warehouses/transfer
    actually lets stock move between warehouses; nothing else has been
    updated to let a user pick a warehouse per-transaction yet."""
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, default="")
    is_default = Column(Boolean, default=False)


class StockLevel(Base):
    __tablename__ = "stock_levels"
    __table_args__ = (UniqueConstraint("product_id", "warehouse_id", name="uq_stock_product_warehouse"),)
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    quantity = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=3)

    product = relationship("Product", back_populates="stock_levels")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    change = Column(Integer, nullable=False)
    reason = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
