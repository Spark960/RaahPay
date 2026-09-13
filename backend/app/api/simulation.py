from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import pandas as pd

from app.core.database import get_session
from app.models import Borrower, Loan, Transaction
from app.schemas.simulation import StressTestRequest
from app.services.simulation import run_stress_test

router = APIRouter(prefix="/simulate", tags=["simulation"])


@router.post("/stress-test")
def stress_test(req: StressTestRequest, session: Session = Depends(get_session)):
    """Run a revenue shock simulation and compare Dynamic vs Fixed EMI outcomes."""
    b = session.get(Borrower, req.borrower_id)
    if not b:
        raise HTTPException(status_code=404, detail="Borrower not found")

    loan = session.exec(select(Loan).where(Loan.borrower_id == req.borrower_id)).first()
    if not loan:
        raise HTTPException(status_code=404, detail="No loan found for borrower")

    txns = session.exec(
        select(Transaction).where(Transaction.borrower_id == req.borrower_id)
        .order_by(Transaction.transaction_date)
    ).all()
    df = pd.DataFrame([{"date": t.transaction_date, "amount": t.amount} for t in txns])
    daily = df.groupby("date")["amount"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.asfreq("D", fill_value=0)

    result = run_stress_test(
        daily_net=daily,
        shock_pct=req.shock_pct,
        shock_duration_days=req.shock_duration_days,
        principal=loan.principal,
        annual_rate=loan.annual_interest_rate,
        base_emi=loan.base_emi,
        tenure_months=loan.original_tenure_months,
        disbursement_date=loan.disbursement_date,
    )
    return result
