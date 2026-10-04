import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class OrderStatus(str, enum.Enum):
    new = "new"
    packing = "packing"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    channel = Column(String, default="line")  # Phase 1: manual/line. Phase 3 adds shopee/lazada etc.
    status = Column(Enum(OrderStatus), default=OrderStatus.new)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    payment_slip_url = Column(String, nullable=True)
    total_amount = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0)

    order = relationship("Order", back_populates="items")
