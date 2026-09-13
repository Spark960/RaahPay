from pydantic import BaseModel
from typing import Optional


class StressTestRequest(BaseModel):
    borrower_id: int
    shock_pct: float = -0.40           # e.g. -0.40 = -40% revenue
    shock_duration_days: int = 30

    class Config:
        json_schema_extra = {
            "example": {
                "borrower_id": 1,
                "shock_pct": -0.40,
                "shock_duration_days": 30,
            }
        }
