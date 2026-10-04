import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class JobStatus(str, enum.Enum):
    quoted = "quoted"
    approved = "approved"
    in_progress = "in_progress"
    done = "done"


class RepairJob(Base):
    """Phase 2 — workshop job management: quotation -> mechanic approval -> in-progress -> done."""
    __tablename__ = "repair_jobs"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    bike_description = Column(String)
    description = Column(String)
    mechanic = Column(String, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.quoted)
    quoted_amount = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer", back_populates="repair_jobs")
