"""
CUSUM-based Early Warning System for financial distress detection.

CUSUM statistic: S_t = max(0, S_{t-1} + (x_t - mu - k))
When S_t > h, a stress alert is triggered.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from app.core.config import settings


def detect_stress(daily_net: pd.Series) -> dict:
    """
    Run CUSUM detector on daily net cash flow.
    Returns list of alert events and current stress status.
    """
    if len(daily_net) < 7:
        return {"is_stressed": False, "alerts": [], "cusum_series": []}

    values = daily_net.fillna(0).values
    mu = np.mean(values)
    sigma = np.std(values) if np.std(values) > 0 else 1.0

    # Standardize
    z = (values - mu) / sigma

    # CUSUM for negative shifts (deterioration)
    k = 0.5   # slack (sensitivity)
    h = settings.cusum_threshold

    S = np.zeros(len(z))
    for t in range(1, len(z)):
        S[t] = max(0, S[t - 1] + (-z[t] - k))  # negative CUSUM = downward shift

    alerts = []
    in_alert = False
    alert_start = None

    for t in range(len(S)):
        if S[t] > h and not in_alert:
            in_alert = True
            alert_start = t
            alert_date = daily_net.index[t]
            alerts.append({
                "type": "stress_onset",
                "date": str(alert_date.date()),
                "severity": "high" if S[t] > h * 1.5 else "moderate",
                "cusum_value": round(float(S[t]), 2),
                "message": f"Financial distress signal detected — cash flow declining significantly",
            })
        elif S[t] <= h and in_alert:
            in_alert = False
            recovery_date = daily_net.index[t]
            alerts.append({
                "type": "stress_recovery",
                "date": str(recovery_date.date()),
                "severity": "info",
                "cusum_value": round(float(S[t]), 2),
                "message": f"Cash flow recovering — stress signal cleared",
            })

    current_stress = bool(S[-1] > h)

    dates = daily_net.index.strftime("%Y-%m-%d").tolist()
    cusum_series = [{"date": d, "value": round(float(v), 2)} for d, v in zip(dates, S)]

    return {
        "is_stressed": current_stress,
        "current_cusum": round(float(S[-1]), 2),
        "threshold": h,
        "alerts": alerts[-5:],  # last 5 alerts
        "cusum_series": cusum_series,
    }
