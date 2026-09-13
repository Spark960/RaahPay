from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import pandas as pd

from app.core.database import get_session
from app.models import Loan, Repayment, Borrower, Transaction
from app.services.dynamic_scheduler import compute_dynamic_schedule, compute_fixed_schedule
from app.services.time_series import forecast as ts_forecast

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/{loan_id}/schedule")
def get_loan_schedule(loan_id: int, session: Session = Depends(get_session)):
    """Current dynamic repayment schedule for a loan."""
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Load borrower transactions for forecast
    txns = session.exec(
        select(Transaction).where(Transaction.borrower_id == loan.borrower_id)
        .order_by(Transaction.transaction_date)
    ).all()
    df = pd.DataFrame([{"date": t.transaction_date, "amount": t.amount} for t in txns])
    daily = df.groupby("date")["amount"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.asfreq("D", fill_value=0)

    fc = ts_forecast(daily, horizon_days=loan.original_tenure_months * 30)
    schedule = compute_dynamic_schedule(
        principal=loan.principal,
        annual_rate=loan.annual_interest_rate,
        base_emi=loan.base_emi,
        forecast_p50=fc["p50"],
        forecast_dates=fc["forecast_dates"],
        disbursement_date=loan.disbursement_date,
    )

    repayments = session.exec(
        select(Repayment).where(Repayment.loan_id == loan_id)
        .order_by(Repayment.period_number)
    ).all()

    return {
        "loan_id": loan_id,
        "principal": loan.principal,
        "base_emi": loan.base_emi,
        "annual_interest_rate": loan.annual_interest_rate,
        "dynamic_schedule": schedule,
        "historical_repayments": [
            {
                "period": r.period_number,
                "due_date": str(r.due_date),
                "scheduled_amount": r.scheduled_amount,
                "actual_amount": r.actual_amount,
                "status": r.status,
                "adjustment_reason": r.adjustment_reason,
            }
            for r in repayments
        ],
    }


@router.get("/{loan_id}/schedule/comparison")
def get_schedule_comparison(loan_id: int, session: Session = Depends(get_session)):
    """Side-by-side: Dynamic schedule vs Traditional fixed EMI."""
    loan = session.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    txns = session.exec(
        select(Transaction).where(Transaction.borrower_id == loan.borrower_id)
        .order_by(Transaction.transaction_date)
    ).all()
    df = pd.DataFrame([{"date": t.transaction_date, "amount": t.amount} for t in txns])
    daily = df.groupby("date")["amount"].sum()
    daily.index = pd.to_datetime(daily.index)
    daily = daily.asfreq("D", fill_value=0)

    fc = ts_forecast(daily, horizon_days=loan.original_tenure_months * 30)

    dynamic = compute_dynamic_schedule(
        principal=loan.principal,
        annual_rate=loan.annual_interest_rate,
        base_emi=loan.base_emi,
        forecast_p50=fc["p50"],
        forecast_dates=fc["forecast_dates"],
        disbursement_date=loan.disbursement_date,
    )
    fixed = compute_fixed_schedule(
        principal=loan.principal,
        annual_rate=loan.annual_interest_rate,
        base_emi=loan.base_emi,
        tenure_months=loan.original_tenure_months,
        disbursement_date=loan.disbursement_date,
    )

    return {
        "loan_id": loan_id,
        "base_emi": loan.base_emi,
        "dynamic_schedule": dynamic,
        "fixed_schedule": fixed,
        "summary": {
            "dynamic_total": round(sum(r["dynamic_payment"] for r in dynamic), 2),
            "fixed_total": round(sum(r["fixed_payment"] for r in fixed), 2),
            "dynamic_periods": len(dynamic),
            "fixed_periods": len(fixed),
        },
    }
