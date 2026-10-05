from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="staff")  # owner, admin, mechanic, staff
    is_active = Column(Boolean, default=True)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)  # multi-tenancy FOUNDATION ONLY — not enforced, see models/tenancy.py
