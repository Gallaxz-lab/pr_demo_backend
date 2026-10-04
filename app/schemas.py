from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ---------- Phase 1: catalog ----------
class CompatibilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bike_make: str
    bike_model: str
    year_from: Optional[int]
    year_to: Optional[int]
    notes: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    category: Optional[str]
    price: float
    description: str
    compatibility: List[CompatibilityOut] = []


class ProductCreate(BaseModel):
    sku: str
    name: str
    category: Optional[str] = None
    price: float
    description: str = ""


# ---------- Phase 1: inventory ----------
class StockMovementCreate(BaseModel):
    product_id: int
    change: int
    reason: str = ""


class StockMovementOut(StockMovementCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Phase 1: customers ----------
class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    line_user_id: Optional[str] = None


class CustomerOut(CustomerCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Phase 1: orders ----------
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    customer_id: int
    channel: str = "line"
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    channel: str
    status: str
    payment_status: str
    total_amount: float
    created_at: datetime


class PaymentVerify(BaseModel):
    verified: bool
    note: Optional[str] = None


# ---------- Phase 1: AI Q&A ----------
class QARequest(BaseModel):
    question: str
    channel: str = "line"
    customer_line_id: Optional[str] = None


class QAResponse(BaseModel):
    answer: str
    grounded_sku: Optional[str] = None
    stock_at_answer_time: Optional[int] = None


# ---------- Phase 2: workshop ----------
class RepairJobCreate(BaseModel):
    customer_id: int
    bike_description: str
    description: str
    quoted_amount: float = 0


class RepairJobOut(RepairJobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    mechanic: Optional[str]
    status: str
    created_at: datetime


# ---------- Phase 3: finance ----------
class SettlementImportCreate(BaseModel):
    channel: str
    reference: str
    gross_amount: float
    fees: float = 0


class InvoiceOcrRequest(BaseModel):
    image_base64: str
    media_type: str = "image/jpeg"  # e.g. image/jpeg, image/png
