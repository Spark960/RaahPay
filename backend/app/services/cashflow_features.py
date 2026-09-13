"""
Cash flow feature extraction pipeline.
Computes ~15 features from a borrower's transaction history.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Any


def extract_features(df: pd.DataFrame, base_emi: float) -> dict[str, Any]:
    """
    df: DataFrame with columns [transaction_date, amount]
         positive = inflow, negative = outflow
    Returns dict of engineered features.
    """
    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df = df.sort_values("transaction_date")

    daily = df.groupby("transaction_date")["amount"].sum().reset_index()
    daily.columns = ["date", "net"]
    daily = daily.set_index("date").asfreq("D", fill_value=0)

    inflows = df[df["amount"] > 0].groupby("transaction_date")["amount"].sum().reindex(daily.index, fill_value=0)
    outflows = df[df["amount"] < 0].groupby("transaction_date")["amount"].sum().abs().reindex(daily.index, fill_value=0)

    net = daily["net"]
    balance = net.cumsum()

    # ── Core metrics ─────────────────────────────────────
    avg_monthly_inflow = inflows.sum() / max(1, len(inflows) / 30)
    avg_monthly_outflow = outflows.sum() / max(1, len(outflows) / 30)

    # Free Discretionary Cash Flow
    fdcf = avg_monthly_inflow - avg_monthly_outflow

    # Debt Service Coverage Ratio
    dscr = fdcf / base_emi if base_emi > 0 else 0.0

    # Cash Buffer Days: avg balance / avg daily outflow
    avg_daily_outflow = outflows.mean() if outflows.mean() > 0 else 1
    avg_balance = balance.mean()
    cash_buffer_days = avg_balance / avg_daily_outflow

    # Inflow Coefficient of Variation
    monthly_inflows = inflows.resample("ME").sum()
    cv_inflow = (monthly_inflows.std() / monthly_inflows.mean()) if monthly_inflows.mean() > 0 else 0

    # Seasonality Ratio
    if len(monthly_inflows) >= 2:
        seasonality_ratio = monthly_inflows.min() / monthly_inflows.max() if monthly_inflows.max() > 0 else 0
    else:
        seasonality_ratio = 1.0

    # Balance Depletion Speed: slope of cumulative balance (negative = depleting)
    x = np.arange(len(balance))
    slope, _ = np.polyfit(x, balance.values, 1) if len(balance) > 1 else (0, 0)
    balance_depletion_speed = slope

    # Zero/negative cash day proportion
    zero_cash_days = (net <= 0).sum() / max(1, len(net))

    # 30-day rolling volatility
    rolling_vol = net.rolling(30).std().mean()

    # Recent trend: last 30 days avg vs overall avg
    recent_avg = net.tail(30).mean()
    overall_avg = net.mean()
    recent_trend_ratio = recent_avg / overall_avg if overall_avg != 0 else 1.0

    # Stress days: net < -50% of avg monthly outflow / 30
    daily_expense_threshold = avg_monthly_outflow * 0.5 / 30
    stress_days_pct = (net < -daily_expense_threshold).sum() / max(1, len(net))

    # Max drawdown
    cum_max = balance.cummax()
    drawdown = (cum_max - balance) / (cum_max.abs() + 1e-9)
    max_drawdown = drawdown.max()

    return {
        "avg_monthly_inflow": round(float(avg_monthly_inflow), 2),
        "avg_monthly_outflow": round(float(avg_monthly_outflow), 2),
        "fdcf": round(float(fdcf), 2),                              # Free Discretionary Cash Flow
        "dscr": round(float(dscr), 3),                              # Debt Service Coverage Ratio
        "cash_buffer_days": round(float(cash_buffer_days), 1),
        "cv_inflow": round(float(cv_inflow), 3),                    # Coefficient of variation
        "seasonality_ratio": round(float(seasonality_ratio), 3),   # min/max month
        "balance_depletion_speed": round(float(balance_depletion_speed), 4),
        "zero_cash_days_pct": round(float(zero_cash_days), 3),
        "rolling_volatility_30d": round(float(rolling_vol), 2),
        "recent_trend_ratio": round(float(recent_trend_ratio), 3),
        "stress_days_pct": round(float(stress_days_pct), 3),
        "max_drawdown": round(float(max_drawdown), 3),
        "base_emi": round(float(base_emi), 2),
        "emi_to_income_ratio": round(float(base_emi / avg_monthly_inflow), 3) if avg_monthly_inflow > 0 else 0,
    }
