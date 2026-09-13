from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Borrower(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    persona_type: str  # "vendor" | "farmer" | "gig_worker"
    base_monthly_income: float
    location: str
    registered_at: date
    status: str = "active"  # "active" | "defaulted" | "completed"
