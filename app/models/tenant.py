from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class Shop(Base):
    """
    Multi-tenancy — FOUNDATION ONLY. This table plus AdminUser.shop_id
    (see user.py) is the seed of the pattern. A real multi-tenant system
    would repeat shop_id scoping across every table (products, orders,
    customers, the entire ledger — everything) and filter every single
    query by the logged-in user's shop. That mechanical-but-substantial
    change is deliberately deferred until it's a confirmed business
    decision (sell to one shop vs many), not forgotten or skipped by
    accident.
    """
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
