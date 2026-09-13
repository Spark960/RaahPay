from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models import Borrower, Loan, RiskAssessment
import pandas as pd

router = APIRouter(prefix="/borrowers", tags=["borrowers"])


def _get_borrower_or_404(borrower_id: int, session: Session) -> Borrower:
    b = session.get(Borrower, borrower_id)
    if not b:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return b


@router.get("/")
def list_borrowers(session: Session = Depends(get_session)):
    borrowers = session.exec(select(Borrower)).all()
    result = []
    for b in borrowers:
        loan = session.exec(select(Loan).where(Loan.borrower_id == b.id)).first()
        risk = session.exec(
            select(RiskAssessment).where(RiskAssessment.borrower_id == b.id)
            .order_by(RiskAssessment.assessment_date.desc())
        ).first()
        result.append({
            "id": b.id,
            "name": b.name,
            "persona_type": b.persona_type,
            "base_monthly_income": b.base_monthly_income,
            "location": b.location,
            "registered_at": str(b.registered_at),
            "status": b.status,
            "loan_id": loan.id if loan else None,
            "loan_principal": loan.principal if loan else None,
            "base_emi": loan.base_emi if loan else None,
            "risk_tier": risk.risk_tier if risk else None,
            "affordability_score": risk.affordability_score if risk else None,
            "default_probability": risk.default_probability if risk else None,
            "financial_state": risk.financial_state if risk else None,
        })
    return result


@router.get("/{borrower_id}")
def get_borrower(borrower_id: int, session: Session = Depends(get_session)):
    b = _get_borrower_or_404(borrower_id, session)
    loan = session.exec(select(Loan).where(Loan.borrower_id == b.id)).first()
    risk = session.exec(
        select(RiskAssessment).where(RiskAssessment.borrower_id == b.id)
        .order_by(RiskAssessment.assessment_date.desc())
    ).first()
    return {
        "id": b.id,
        "name": b.name,
        "persona_type": b.persona_type,
        "base_monthly_income": b.base_monthly_income,
        "location": b.location,
        "registered_at": str(b.registered_at),
        "status": b.status,
        "loan": {
            "id": loan.id, "principal": loan.principal,
            "annual_interest_rate": loan.annual_interest_rate,
            "original_tenure_months": loan.original_tenure_months,
            "base_emi": loan.base_emi,
            "disbursement_date": str(loan.disbursement_date),
            "status": loan.status,
        } if loan else None,
        "risk": {
            "default_probability": risk.default_probability,
            "affordability_score": risk.affordability_score,
            "risk_tier": risk.risk_tier,
            "financial_state": risk.financial_state,
        } if risk else None,
    }
