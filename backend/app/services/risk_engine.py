"""
Risk Engine: LightGBM-based default probability scorer + TreeSHAP explanations
+ Dynamic Affordability Score (DAS).

For hackathon: we train a simple LightGBM model on synthetic feature data,
then use it for real-time scoring with SHAP explanations.
"""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from typing import Any

try:
    import lightgbm as lgb
    import shap
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

# ── Synthetic training data for the model ───────────────────────────────────

def _make_training_data() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Generate synthetic training data representing different risk profiles.
    Features map to real-world microfinance risk factors.
    """
    np.random.seed(42)
    n = 2000

    feature_names = [
        "dscr", "cv_inflow", "seasonality_ratio", "cash_buffer_days",
        "zero_cash_days_pct", "balance_depletion_speed_norm",
        "stress_days_pct", "max_drawdown", "recent_trend_ratio",
        "emi_to_income_ratio", "rolling_volatility_norm", "fdcf_norm"
    ]

    # Generate features with risk-correlated structure
    dscr = np.random.lognormal(0.3, 0.5, n)
    cv_inflow = np.random.beta(2, 5, n)
    seasonality_ratio = np.random.beta(3, 2, n)
    cash_buffer = np.random.exponential(15, n)
    zero_days = np.random.beta(1, 5, n)
    balance_depl = np.random.normal(0, 1, n)
    stress_days = np.random.beta(1, 8, n)
    max_drawdown = np.random.beta(2, 5, n)
    recent_trend = np.random.normal(1.0, 0.3, n)
    emi_ratio = np.random.beta(3, 5, n)
    rolling_vol = np.abs(np.random.normal(0, 1, n))
    fdcf_norm = np.random.normal(1, 0.5, n)

    X = np.column_stack([
        dscr, cv_inflow, seasonality_ratio, cash_buffer, zero_days,
        balance_depl, stress_days, max_drawdown, recent_trend,
        emi_ratio, rolling_vol, fdcf_norm
    ])

    # Default probability: high when DSCR low, CV high, buffer days low
    log_odds = (
        -2.0 * np.log(np.clip(dscr, 0.1, 10))
        + 3.0 * cv_inflow
        - 0.05 * cash_buffer
        + 4.0 * stress_days
        + 2.0 * max_drawdown
        + 2.0 * emi_ratio
        - 1.5 * np.clip(recent_trend, 0, 3)
        + np.random.normal(0, 0.5, n)
    )
    prob = 1 / (1 + np.exp(-log_odds))
    y = (prob > 0.5).astype(int)

    return X, y, feature_names


# Train once at module load
_FEATURE_NAMES: list[str] = []
_MODEL = None
_EXPLAINER = None

def _ensure_model():
    global _MODEL, _EXPLAINER, _FEATURE_NAMES
    if _MODEL is not None:
        return
    if not HAS_LGBM:
        return

    X, y, names = _make_training_data()
    _FEATURE_NAMES = names

    dtrain = lgb.Dataset(X, label=y)
    params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_name": names,
        "verbose": -1,
    }
    _MODEL = lgb.train(params, dtrain, num_boost_round=100)
    _EXPLAINER = shap.TreeExplainer(_MODEL)


# ── Feature normalisation helper ─────────────────────────────────────────────

def _features_to_vector(features: dict[str, Any]) -> np.ndarray:
    """Map extracted cash flow features to the model's feature vector."""
    return np.array([[
        features.get("dscr", 1.0),
        features.get("cv_inflow", 0.3),
        features.get("seasonality_ratio", 0.7),
        min(features.get("cash_buffer_days", 10), 90),
        features.get("zero_cash_days_pct", 0.1),
        np.clip(features.get("balance_depletion_speed", 0) / max(abs(features.get("avg_monthly_inflow", 1)), 1), -5, 5),
        features.get("stress_days_pct", 0.05),
        features.get("max_drawdown", 0.2),
        features.get("recent_trend_ratio", 1.0),
        features.get("emi_to_income_ratio", 0.25),
        features.get("rolling_volatility_30d", 50) / max(features.get("avg_monthly_inflow", 1), 1),
        features.get("fdcf", 100) / max(features.get("avg_monthly_inflow", 1), 1),
    ]])


# ── Scoring functions ─────────────────────────────────────────────────────────

_SHAP_LABELS = {
    "dscr": "Debt Service Coverage Ratio",
    "cv_inflow": "Income Volatility",
    "seasonality_ratio": "Seasonal Income Consistency",
    "cash_buffer_days": "Cash Buffer (Days)",
    "zero_cash_days_pct": "Zero-Income Day Frequency",
    "balance_depletion_speed_norm": "Balance Depletion Speed",
    "stress_days_pct": "Financial Stress Days",
    "max_drawdown": "Maximum Balance Drawdown",
    "recent_trend_ratio": "Recent Income Trend",
    "emi_to_income_ratio": "EMI-to-Income Burden",
    "rolling_volatility_norm": "30-Day Cash Flow Volatility",
    "fdcf_norm": "Free Discretionary Cash Flow",
}

_RISK_ADVICE = {
    "dscr": "Improve by increasing income or reducing fixed expenses.",
    "cv_inflow": "Smooth income by diversifying revenue sources.",
    "cash_buffer_days": "Build a 15-day cash buffer before next assessment.",
    "stress_days_pct": "Reduce high-expense days; review variable costs.",
    "emi_to_income_ratio": "Consider smaller loan or longer tenure to reduce burden.",
    "max_drawdown": "Avoid large one-time withdrawals; maintain balance stability.",
}


def score_risk(features: dict[str, Any]) -> dict:
    """
    Score default risk and generate SHAP explanations.
    Returns default_probability, risk_tier, shap_values, reason_codes.
    """
    _ensure_model()

    if not HAS_LGBM or _MODEL is None:
        return _heuristic_score(features)

    X = _features_to_vector(features)
    prob = float(_MODEL.predict(X)[0])

    # SHAP
    shap_vals = _EXPLAINER.shap_values(X)[0]  # shape: (n_features,)
    shap_list = [
        {
            "feature": _FEATURE_NAMES[i],
            "label": _SHAP_LABELS.get(_FEATURE_NAMES[i], _FEATURE_NAMES[i]),
            "shap_value": round(float(shap_vals[i]), 4),
            "feature_value": round(float(X[0, i]), 4),
            "direction": "risk_increasing" if shap_vals[i] > 0 else "risk_reducing",
            "advice": _RISK_ADVICE.get(_FEATURE_NAMES[i], ""),
        }
        for i in range(len(_FEATURE_NAMES))
    ]
    # Sort by absolute impact
    shap_list.sort(key=lambda x: abs(x["shap_value"]), reverse=True)

    risk_tier = _prob_to_tier(prob)

    return {
        "default_probability": round(prob, 4),
        "risk_tier": risk_tier,
        "shap_explanations": shap_list[:6],  # top 6
    }


def compute_das(features: dict[str, Any], default_prob: float) -> float:
    """
    Dynamic Affordability Score (DAS) ∈ [0, 100].
    Higher = more affordable / creditworthy.
    """
    dscr_score = min(100, max(0, (features.get("dscr", 0) - 0.5) / 2.5 * 100))
    buffer_score = min(100, max(0, features.get("cash_buffer_days", 0) / 30 * 100))
    volatility_penalty = features.get("cv_inflow", 0.5) * 50
    risk_penalty = default_prob * 60
    trend_bonus = max(0, (features.get("recent_trend_ratio", 1) - 1) * 20)

    das = (0.35 * dscr_score + 0.25 * buffer_score + 0.15 * (100 - volatility_penalty) +
           0.15 * (100 - risk_penalty) + 0.10 * min(100, trend_bonus + 50))

    return round(float(np.clip(das, 0, 100)), 1)


def _prob_to_tier(prob: float) -> str:
    if prob < 0.15:
        return "low"
    elif prob < 0.35:
        return "moderate"
    elif prob < 0.60:
        return "high"
    return "critical"


def _heuristic_score(features: dict[str, Any]) -> dict:
    """Fallback if LightGBM not available."""
    dscr = features.get("dscr", 1.0)
    cv = features.get("cv_inflow", 0.3)
    buf = features.get("cash_buffer_days", 10)

    prob = max(0.05, min(0.95, 0.5 - 0.15 * dscr + 0.2 * cv - 0.005 * buf))
    return {
        "default_probability": round(prob, 4),
        "risk_tier": _prob_to_tier(prob),
        "shap_explanations": [
            {"feature": "dscr", "label": "Debt Service Coverage Ratio",
             "shap_value": -0.15 * dscr, "feature_value": dscr,
             "direction": "risk_reducing" if dscr > 1 else "risk_increasing", "advice": ""}
        ],
    }
