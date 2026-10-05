from sqlalchemy import Column, Integer, String
from app.database import Base


class Warehouse(Base):
    """FOUNDATION ONLY — schema exists and the transfer endpoint uses it, but
    order fulfillment and procurement receiving elsewhere in the app still
    read/write stock by product_id alone, which only stays correct as long
    as each product has exactly one stock row (today's reality, enforced by
    always writing to the seeded 'Main' warehouse). Only matters once a
    second physical location actually holds stock."""
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    address = Column(String, default="")
