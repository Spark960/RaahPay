from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import pandas as pd
import json
from datetime import date

from app.core.database import get_session
from app.models import Borrower, Loan, Transaction, RiskAssessment
from app.services.cashflow_features import extract_features
from app.services.risk_engine import score_risk, compute_das
from app.services.early_warning import detect_stress

router = APIRouter(prefix="/borrowers", tags=["risk"])


def _load_tx_df(borrower_id: int, session: Session) -> pd.DataFrame:
    txns = session.exec(
        select(Transaction).where(Transaction.borrower_id == borrower_id)
        .order_by(Transaction.transaction_date)
    ).all()
    if not txns:
        raise HTTPException(status_code=404, detail="No transactions found")
    return pd.DataFrame([{"transaction_date": t.transaction_date, "amount": t.amount} for t in txns])


@router.get("/{borrower_id}/risk")
def get_risk(borrower_id: int, session: Session = Depends(get_session)):
    """Risk score + SHAP explanations + DAS score."""
    b = session.get(Borrower, borrower_id)
    if not b:
        raise HTTPException(status_code=404, detail="Borrower not found")

    loan = session.exec(select(Loan).where(Loan.borrower_id == borrower_id)).first()
    base_emi = loan.base_emi if loan else 1.0

    df = _load_tx_df(borrower_id, session)
    features = extract_features(df, base_emi)
    risk_result = score_risk(features)
    das = compute_das(features, risk_result["default_probability"])

    # Financial state heuristic (mock HMM for demo)
    prob = risk_result["default_probability"]
    trend = features.get("recent_trend_ratio", 1.0)
    if prob < 0.15 and trend > 1.0:
        fin_state = "thriving"
    elif prob < 0.25:
        fin_state = "stable"
    elif prob < 0.45 and trend < 0.9:
        fin_state = "stressed"
    elif prob >= 0.45:
        fin_state = "deteriorating"
    else:
        fin_state = "recovering"

    # Persist risk assessment
    assessment = RiskAssessment(
        borrower_id=borrower_id,
        assessment_date=date.today(),
        default_probability=risk_result["default_probability"],
        affordability_score=das,
        risk_tier=risk_result["risk_tier"],
        shap_explanations=json.dumps(risk_result["shap_explanations"]),
        early_warnings=json.dumps([]),
        financial_state=fin_state,
    )
    session.add(assessment)
    session.commit()

    return {
        "borrower_id": borrower_id,
        "default_probability": risk_result["default_probability"],
        "risk_tier": risk_result["risk_tier"],
        "affordability_score": das,
        "financial_state": fin_state,
        "shap_explanations": risk_result["shap_explanations"],
        "features": features,
    }


@router.get("/{borrower_id}/alerts")
def get_alerts(borrower_id: int, session: Session = Depends(get_session)):
    """CUSUM-based early warning signals."""
    df = _load_tx_df(borrower_id, session)
    daily = df.groupby("transaction_date")["amount"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.asfreq("D", fill_value=0)
    return detect_stress(daily)
