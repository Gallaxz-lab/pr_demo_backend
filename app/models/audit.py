from sqlalchemy import Column, Integer, String, DateTime, func, Text
from app.database import Base


class AuditLog(Base):
    """Who did what, when. Nothing in the app code deletes or edits these
    rows — an audit trail that can be altered by the same app isn't one."""
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    actor = Column(String, default="system")
    action = Column(String, nullable=False)
    entity = Column(String, nullable=False)
    entity_id = Column(String, default="")
    detail = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
