from pydantic import BaseModel
from typing import Optional
from datetime import date


class BorrowerResponse(BaseModel):
    id: int
    name: str
    persona_type: str
    base_monthly_income: float
    location: str
    registered_at: date
    status: str

    class Config:
        from_attributes = True


class BorrowerSummary(BorrowerResponse):
    """Extended with computed summary fields."""
    loan_id: Optional[int] = None
    loan_principal: Optional[float] = None
    base_emi: Optional[float] = None
    risk_tier: Optional[str] = None
    affordability_score: Optional[float] = None
    default_probability: Optional[float] = None
    financial_state: Optional[str] = None
