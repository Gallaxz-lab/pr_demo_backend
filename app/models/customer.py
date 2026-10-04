from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    line_user_id = Column(String, unique=True, nullable=True)  # Phase 2: links to LINE messaging identity
    notes = Column(String, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="customer")
    repair_jobs = relationship("RepairJob", back_populates="customer")
