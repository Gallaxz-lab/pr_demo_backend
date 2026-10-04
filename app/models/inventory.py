from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class StockLevel(Base):
    __tablename__ = "stock_levels"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=3)

    product = relationship("Product", back_populates="stock_level")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    change = Column(Integer, nullable=False)  # positive = stock in, negative = stock out
    reason = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
