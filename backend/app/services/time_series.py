"""
Time series analytics: STL decomposition + quantile cash flow forecasting.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL


def decompose(daily_net: pd.Series, period: int = 7) -> dict:
    """
    Run STL decomposition on a daily net-cashflow series.
    Returns trend, seasonal, and residual components.
    """
    series = daily_net.copy().fillna(0)

    if len(series) < period * 2:
        # Not enough data — return flat decomposition
        return {
            "dates": series.index.strftime("%Y-%m-%d").tolist(),
            "observed": series.tolist(),
            "trend": series.tolist(),
            "seasonal": [0.0] * len(series),
            "residual": [0.0] * len(series),
        }

    stl = STL(series, period=period, robust=True)
    result = stl.fit()

    return {
        "dates": series.index.strftime("%Y-%m-%d").tolist(),
        "observed": [round(float(v), 2) for v in series.values],
        "trend": [round(float(v), 2) for v in result.trend],
        "seasonal": [round(float(v), 2) for v in result.seasonal],
        "residual": [round(float(v), 2) for v in result.resid],
    }


def forecast(daily_net: pd.Series, horizon_days: int = 90) -> dict:
    """
    Simple quantile forecast using seasonal naive + trend extrapolation.
    Returns P10, P50, P90 bands.
    """
    series = daily_net.copy().fillna(0)
    n = len(series)

    if n < 14:
        # Flat forecast
        flat = float(series.mean())
        return _flat_forecast(series, flat, horizon_days)

    # Decompose
    period = min(7, n // 2)
    try:
        stl = STL(series, period=period, robust=True)
        res = stl.fit()
        trend = res.trend
        seasonal = res.seasonal
        residual = res.resid
    except Exception:
        flat = float(series.mean())
        return _flat_forecast(series, flat, horizon_days)

    # Extrapolate trend using linear fit on last 60 days
    trend_window = trend[-min(60, n):]
    x = np.arange(len(trend_window))
    slope, intercept = np.polyfit(x, trend_window, 1)

    # Seasonal pattern: repeat last full cycle
    seasonal_cycle = seasonal[-period:].tolist()

    resid_std = float(residual.std()) if residual.std() > 0 else 1.0

    last_date = series.index[-1]
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D")

    p50, p10, p90 = [], [], []
    for i, fd in enumerate(future_dates):
        trend_val = (len(trend_window) + i) * slope + intercept
        seasonal_val = seasonal_cycle[i % period]
        base = trend_val + seasonal_val
        p50.append(round(float(base), 2))
        p10.append(round(float(base - 1.645 * resid_std), 2))
        p90.append(round(float(base + 1.645 * resid_std), 2))

    # Historical portion for chart continuity
    hist_dates = series.index.strftime("%Y-%m-%d").tolist()
    hist_vals = [round(float(v), 2) for v in series.values]

    return {
        "historical_dates": hist_dates,
        "historical": hist_vals,
        "forecast_dates": future_dates.strftime("%Y-%m-%d").tolist(),
        "p50": p50,
        "p10": p10,
        "p90": p90,
    }


def _flat_forecast(series: pd.Series, flat_val: float, horizon_days: int) -> dict:
    last_date = series.index[-1]
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon_days, freq="D")
    return {
        "historical_dates": series.index.strftime("%Y-%m-%d").tolist(),
        "historical": [round(float(v), 2) for v in series.values],
        "forecast_dates": future_dates.strftime("%Y-%m-%d").tolist(),
        "p50": [round(flat_val, 2)] * horizon_days,
        "p10": [round(flat_val * 0.7, 2)] * horizon_days,
        "p90": [round(flat_val * 1.3, 2)] * horizon_days,
    }
