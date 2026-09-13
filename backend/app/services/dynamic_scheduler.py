"""
Dynamic Repayment Scheduler — Bounded Sweep Engine.

Formula:
  Installment_t = clip(α × NetInflow_t × S_t,  I_min,  I_max)

where:
  α     = sweep fraction (default 0.20)
  S_t   = seasonality factor for period t  (from STL)
  I_min = base_emi × min_payment_factor
  I_max = base_emi × max_payment_factor
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from datetime import date, timedelta
from app.core.config import settings


def compute_dynamic_schedule(
    principal: float,
    annual_rate: float,
    base_emi: float,
    forecast_p50: list[float],
    forecast_dates: list[str],
    seasonal_factors: list[float] | None = None,
    stress_active: bool = False,
    disbursement_date: date | None = None,
) -> list[dict]:
    """
    Compute a dynamic repayment schedule using forecasted cash flows.

    Returns list of monthly repayment dicts.
    """
    alpha = settings.sweep_alpha
    i_min = base_emi * (settings.min_payment_factor * 0.7 if stress_active else settings.min_payment_factor)
    i_max = base_emi * settings.max_payment_factor

    # Aggregate daily forecast into monthly buckets
    fc_df = pd.DataFrame({"date": pd.to_datetime(forecast_dates), "p50": forecast_p50})
    fc_df = fc_df.set_index("date")
    monthly_net = fc_df["p50"].resample("ME").sum()

    avg_monthly_net = monthly_net.mean()
    if avg_monthly_net <= 0:
        avg_monthly_net = 1.0

    r_monthly = annual_rate / 12
    balance = principal
    schedule = []

    start_date = disbursement_date or date.today()

    for i, (month_end, monthly_inflow) in enumerate(monthly_net.items(), start=1):
        if balance <= 0:
            break

        # Seasonality factor from STL (or neutral 1.0)
        s_t = seasonal_factors[i - 1] if seasonal_factors and i <= len(seasonal_factors) else 1.0
        s_t = max(0.5, min(2.0, s_t))  # sanity clamp

        # Ratio-based sweep (scale EMI by how good this month is compared to average)
        ratio = max(0, monthly_inflow) / avg_monthly_net
        raw_payment = base_emi * ratio * s_t
        payment = float(np.clip(raw_payment, i_min, i_max))

        # Interest for this period
        interest = balance * r_monthly
        principal_comp = max(0, payment - interest)
        balance = max(0, balance - principal_comp)

        reason = "standard"
        if payment <= i_min * 1.05:
            reason = "stress_detected" if stress_active else "seasonal_low"
        elif payment >= i_max * 0.95:
            reason = "surplus_available"

        due_date = start_date + timedelta(days=30 * i)

        schedule.append({
            "period": i,
            "due_date": due_date.isoformat(),
            "dynamic_payment": round(payment, 2),
            "base_emi": round(base_emi, 2),
            "interest_component": round(interest, 2),
            "principal_component": round(principal_comp, 2),
            "remaining_balance": round(balance, 2),
            "adjustment_reason": reason,
            "monthly_forecast_inflow": round(float(monthly_inflow), 2),
            "affordability_ratio": round(payment / base_emi, 3),
        })

        if balance == 0:
            break

    return schedule


def compute_fixed_schedule(
    principal: float,
    annual_rate: float,
    base_emi: float,
    tenure_months: int,
    disbursement_date: date | None = None,
) -> list[dict]:
    """Standard fixed EMI schedule for comparison."""
    r = annual_rate / 12
    balance = principal
    schedule = []
    start_date = disbursement_date or date.today()

    for i in range(1, tenure_months + 1):
        interest = balance * r
        principal_comp = base_emi - interest
        balance = max(0, balance - principal_comp)
        due_date = start_date + timedelta(days=30 * i)

        schedule.append({
            "period": i,
            "due_date": due_date.isoformat(),
            "fixed_payment": round(base_emi, 2),
            "interest_component": round(interest, 2),
            "principal_component": round(principal_comp, 2),
            "remaining_balance": round(balance, 2),
        })

    return schedule
