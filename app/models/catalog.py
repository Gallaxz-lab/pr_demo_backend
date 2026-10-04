from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    price = Column(Float, nullable=False, default=0)
    cost_price = Column(Float, default=0)  # enables real COGS / inventory valuation in the ledger
    description = Column(Text, default="")

    compatibility = relationship("Compatibility", back_populates="product", cascade="all, delete-orphan")
    stock_level = relationship("StockLevel", back_populates="product", uselist=False, cascade="all, delete-orphan")


class Compatibility(Base):
    __tablename__ = "compatibility_records"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    bike_make = Column(String, nullable=False)
    bike_model = Column(String, nullable=False)
    year_from = Column(Integer)
    year_to = Column(Integer)
    notes = Column(String, default="")

    product = relationship("Product", back_populates="compatibility")
