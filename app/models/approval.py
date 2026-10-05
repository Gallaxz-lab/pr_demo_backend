import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, func, Enum
from app.database import Base


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Approval(Base):
    """
    FOUNDATION ONLY. The ฿10,000 threshold in approval_service.py is a
    placeholder — real thresholds and who approves what need an actual
    policy decision from the shop owner, not a guess.
    """
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    amount = Column(Float, default=0)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.pending)
    requested_by = Column(String, default="")
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
