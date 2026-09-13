from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Repayment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    loan_id: int = Field(foreign_key="loan.id")
    period_number: int
    due_date: date
    scheduled_amount: float
    actual_amount: float = 0.0
    principal_component: float = 0.0
    interest_component: float = 0.0
    remaining_balance: float = 0.0
    status: str = "pending"  # "paid" | "partial" | "missed" | "deferred" | "pending"
    adjustment_reason: str = "standard"  # "seasonal_low" | "stress_detected" | "surplus_available" | "standard"
