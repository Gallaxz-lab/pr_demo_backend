from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, func
from app.database import Base


class Employee(Base):
    """Foundation only — no org structure, roles, or leave tracking."""
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, default="mechanic")
    monthly_salary = Column(Float, default=0)


class Payslip(Base):
    """
    DEMO ESTIMATOR ONLY. ssf_deduction uses a placeholder rate/cap that has
    NOT been verified against current Thai Social Security Fund rules.
    withholding_tax is deliberately left at 0 rather than faking progressive
    PND.1 bracket logic — see payroll_service.py. Do NOT use for real
    payroll without a qualified accountant reviewing current rates first.
    """
    __tablename__ = "payslips"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    period = Column(String)  # e.g. "2026-10"
    gross_pay = Column(Float, default=0)
    ssf_deduction = Column(Float, default=0)
    withholding_tax = Column(Float, default=0)
    net_pay = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
