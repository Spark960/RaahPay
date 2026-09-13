from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id")
    principal: float
    annual_interest_rate: float = 0.18  # 18% typical microfinance
    original_tenure_months: int = 12
    adjusted_tenure_months: int = 12
    base_emi: float
    disbursement_date: date
    status: str = "active"  # "active" | "completed" | "defaulted" | "restructured"
    schedule_type: str = "dynamic"  # "dynamic" | "fixed"
