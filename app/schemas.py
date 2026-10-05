from datetime import datetime, date
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


class InvoiceRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    vendor: str
    amount: float
    status: str
    created_at: datetime


class SettlementImportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel: str
    reference: str
    net_amount: float
    matched_order_id: Optional[int]
    imported_at: datetime


# ---------- ERP core: procurement ----------
class SupplierCreate(BaseModel):
    name: str
    contact: str = ""
    phone: str = ""


class SupplierOut(SupplierCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class POItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_cost: float


class POItemOut(POItemCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[POItemCreate]


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    supplier_id: int
    status: str
    created_at: datetime
    items: List[POItemOut] = []


# ---------- Foundation: multi-warehouse ----------
class WarehouseCreate(BaseModel):
    name: str
    address: str = ""
    is_default: bool = False


class StockTransferCreate(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int


class StockTransferOut(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int
    source_remaining: int
    dest_total: int


# ---------- Foundation: receivables / AR ----------
class CustomerInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invoice_number: str
    order_id: Optional[int]
    customer_id: int
    subtotal: float
    vat_amount: float
    total_amount: float
    status: str
    issue_date: datetime
    due_date: Optional[datetime]


# ---------- Foundation: payroll (demo estimator only) ----------
class EmployeeCreate(BaseModel):
    name: str
    role: str = "mechanic"
    monthly_salary: float = 0


class EmployeeOut(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PayslipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employee_id: int
    period: str
    gross_pay: float
    ssf_deduction: float
    withholding_tax: float
    net_pay: float
    created_at: datetime


# ---------- Foundation: bank reconciliation ----------
class BankStatementLineCreate(BaseModel):
    statement_date: datetime
    description: str
    amount: float


class BankStatementLineOut(BankStatementLineCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    matched_journal_entry_id: Optional[int]
    imported_at: datetime


# ---------- Foundation: approvals ----------
class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    entity_type: str
    entity_id: int
    amount: float
    status: str
    requested_by: str
    approved_by: Optional[str]
    created_at: datetime


# ---------- Foundation: multi-tenancy ----------
class ShopCreate(BaseModel):
    name: str
    slug: str


class ShopOut(ShopCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Foundations: multi-warehouse ----------
class WarehouseCreate(BaseModel):
    name: str
    address: str = ""


class StockTransfer(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: int


# ---------- Foundations: customer invoicing / AR aging ----------
class CustomerInvoiceCreate(BaseModel):
    customer_id: int
    order_id: Optional[int] = None
    due_in_days: int = 30
    subtotal: float
    vat_amount: float = 0


class CustomerInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invoice_number: str
    customer_id: int
    order_id: Optional[int]
    issue_date: datetime
    due_date: Optional[datetime]
    subtotal: float
    vat_amount: float
    total: float
    status: str
    is_tax_invoice: bool


# ---------- Foundations: payroll (estimate only) ----------
class EmployeeCreate(BaseModel):
    name: str
    role: str = "staff"
    base_salary: float
    start_date: Optional[date] = None


class EmployeeOut(EmployeeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PayrollRunCreate(BaseModel):
    period_start: date
    period_end: date


class PayrollRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    period_start: date
    period_end: date
    created_at: datetime


# ---------- Foundations: bank reconciliation ----------
class BankStatementLineCreate(BaseModel):
    bank_name: str = ""
    statement_date: datetime
    description: str = ""
    amount: float


# ---------- Foundations: multi-tenancy ----------
class ShopCreate(BaseModel):
    name: str
    slug: str
