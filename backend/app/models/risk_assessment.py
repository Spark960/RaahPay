from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field, Column
import sqlalchemy as sa


class RiskAssessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    borrower_id: int = Field(foreign_key="borrower.id")
    assessment_date: date
    default_probability: float
    affordability_score: float  # DAS 0-100
    risk_tier: str  # "low" | "moderate" | "high" | "critical"
    shap_explanations: Optional[str] = Field(default=None, sa_column=Column(sa.Text))  # JSON string
    early_warnings: Optional[str] = Field(default=None, sa_column=Column(sa.Text))    # JSON string
    financial_state: str = "stable"  # "thriving" | "stable" | "stressed" | "deteriorating" | "recovering"
