from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id")
    transaction_date: date
    amount: float  # positive = inflow, negative = outflow
    type: str      # "income" | "expense"
    category: str  # "sales" | "wages" | "rent" | "food" | "inventory" | "utilities" | "other"
    description: str = ""
