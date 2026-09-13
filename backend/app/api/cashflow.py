from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import pandas as pd

from app.core.database import get_session
from app.models import Transaction, Borrower
from app.services.time_series import decompose, forecast as ts_forecast
from app.services.cashflow_features import extract_features
from app.core.config import settings

router = APIRouter(prefix="/borrowers", tags=["cashflow"])


def _load_daily_net(borrower_id: int, session: Session) -> pd.Series:
    txns = session.exec(
        select(Transaction).where(Transaction.borrower_id == borrower_id)
        .order_by(Transaction.transaction_date)
    ).all()
    if not txns:
        raise HTTPException(status_code=404, detail="No transactions found")
    df = pd.DataFrame([{
        "date": t.transaction_date,
        "amount": t.amount
    } for t in txns])
    daily = df.groupby("date")["amount"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.asfreq("D", fill_value=0)
    return daily


@router.get("/{borrower_id}/cashflow")
def get_cashflow(borrower_id: int, session: Session = Depends(get_session)):
    """Raw daily transaction history."""
    daily = _load_daily_net(borrower_id, session)
    return {
        "borrower_id": borrower_id,
        "dates": daily.index.strftime("%Y-%m-%d").tolist(),
        "net_cashflow": [round(float(v), 2) for v in daily.values],
    }


@router.get("/{borrower_id}/cashflow/decomposition")
def get_decomposition(borrower_id: int, session: Session = Depends(get_session)):
    """STL decomposition: trend, seasonal, residual."""
    daily = _load_daily_net(borrower_id, session)
    return decompose(daily)


@router.get("/{borrower_id}/cashflow/forecast")
def get_forecast(
    borrower_id: int,
    horizon: int = 90,
    session: Session = Depends(get_session),
):
    """Cash flow forecast with P10/P50/P90 confidence bands."""
    daily = _load_daily_net(borrower_id, session)
    return ts_forecast(daily, horizon_days=min(horizon, 180))


@router.get("/{borrower_id}/cashflow/features")
def get_features(borrower_id: int, session: Session = Depends(get_session)):
    """Extracted cash flow features used in risk scoring."""
    from app.models import Loan
    daily = _load_daily_net(borrower_id, session)
    loan = session.exec(select(Loan).where(Loan.borrower_id == borrower_id)).first()
    base_emi = loan.base_emi if loan else 1.0
    df = pd.DataFrame({"transaction_date": daily.index, "amount": daily.values})
    return extract_features(df, base_emi)
