from sqlalchemy import Column, Integer, String
from app.database import Base


class Shop(Base):
    """Multi-tenancy FOUNDATION ONLY. This table exists and AdminUser links to
    it, but NO other table (products, orders, inventory, ledger — nothing)
    has a shop_id column, and NO query anywhere is scoped by shop. Data
    isolation is NOT enforced. Do not represent this as multi-tenant-safe —
    that requires scoping every table and every query, which is unbuilt."""
    __tablename__ = "shops"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
