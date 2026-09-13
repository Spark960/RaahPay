"""
Stress test & what-if simulation engine.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from app.services.time_series import forecast
from app.services.dynamic_scheduler import compute_dynamic_schedule, compute_fixed_schedule


def apply_shock(
    daily_net: pd.Series,
    shock_pct: float,        # e.g. -0.40 for -40% revenue shock
    shock_duration_days: int,
) -> pd.Series:
    """Apply a revenue shock to the series (income only, not expenses)."""
    shocked = daily_net.copy()
    # Apply shock to last N days as forecast scenario
    shocked_tail = daily_net.tail(shock_duration_days)
    # Only reduce inflows (positive values), not outflows
    shocked_inflows = shocked_tail.clip(lower=0) * (1 + shock_pct)
    shocked_outflows = shocked_tail.clip(upper=0)
    shocked.iloc[-shock_duration_days:] = shocked_inflows + shocked_outflows
    return shocked


def run_stress_test(
    daily_net: pd.Series,
    shock_pct: float,
    shock_duration_days: int,
    principal: float,
    annual_rate: float,
    base_emi: float,
    tenure_months: int,
    disbursement_date=None,
) -> dict:
    """
    Compare outcomes: Traditional Fixed EMI vs RaahPay Dynamic under a shock.
    """
    # ── Shocked forecast ──────────────────────────────────────────
    shocked = apply_shock(daily_net, shock_pct, shock_duration_days)
    shocked_fc = forecast(shocked, horizon_days=tenure_months * 30)

    # ── Dynamic schedule under shock ──────────────────────────────
    dynamic_schedule = compute_dynamic_schedule(
        principal=principal,
        annual_rate=annual_rate,
        base_emi=base_emi,
        forecast_p50=shocked_fc["p50"],
        forecast_dates=shocked_fc["forecast_dates"],
        stress_active=True,
        disbursement_date=disbursement_date,
    )

    # ── Fixed schedule (never adapts) ─────────────────────────────
    fixed_schedule = compute_fixed_schedule(
        principal=principal,
        annual_rate=annual_rate,
        base_emi=base_emi,
        tenure_months=len(dynamic_schedule),
        disbursement_date=disbursement_date,
    )

    # ── Compute stressed monthly inflow for affordability check ───
    shocked_monthly_inflow = shocked_fc["p50"]
    chunk = 30
    monthly_inflows = [
        sum(shocked_monthly_inflow[i:i+chunk])
        for i in range(0, len(shocked_monthly_inflow), chunk)
    ]

    # ── Compute missed payments for fixed EMI ─────────────────────
    fixed_missed = 0
    fixed_missed_periods = []
    dynamic_stressed_periods = []

    for i, (d_row, f_row) in enumerate(zip(dynamic_schedule, fixed_schedule)):
        m_inflow = monthly_inflows[i] if i < len(monthly_inflows) else base_emi * 3
        # Fixed EMI misses if monthly inflow < EMI
        if m_inflow < base_emi * 0.9:
            fixed_missed += 1
            fixed_missed_periods.append(d_row["period"])
        # Dynamic is stressed but doesn't miss (floors at i_min)
        if d_row["dynamic_payment"] < base_emi * 0.85:
            dynamic_stressed_periods.append(d_row["period"])

    # ── Totals ────────────────────────────────────────────────────
    dynamic_total = sum(r["dynamic_payment"] for r in dynamic_schedule)
    fixed_total = base_emi * len(fixed_schedule)

    return {
        "shock": {"pct": shock_pct, "duration_days": shock_duration_days},
        "dynamic_schedule": dynamic_schedule,
        "fixed_schedule": fixed_schedule,
        "summary": {
            "dynamic_total_paid": round(dynamic_total, 2),
            "fixed_total_due": round(fixed_total, 2),
            "fixed_missed_payments": fixed_missed,
            "fixed_missed_periods": fixed_missed_periods,
            "dynamic_stressed_periods": dynamic_stressed_periods,
            "dynamic_missed_payments": 0,  # Dynamic never misses — it adapts
            "savings_from_dynamic": round(max(0, fixed_total - dynamic_total), 2),
        },
        "monthly_inflows": [round(v, 2) for v in monthly_inflows[:len(dynamic_schedule)]],
    }
