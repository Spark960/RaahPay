# FlowLend — API Design Specification

> Complete endpoint reference for the FastAPI backend.  
> Base URL: `http://localhost:8000/api/v1`  
> Interactive Docs: `http://localhost:8000/docs` (Swagger UI)

---

## Route Groups Overview

| Group | Prefix | Purpose | Endpoints |
|:------|:-------|:--------|:----------|
| **Borrowers** | `/borrowers` | Borrower profiles & portfolio | 3 |
| **Cash Flow** | `/borrowers/{id}/cashflow` | Transactions, decomposition, forecasts | 3 |
| **Loans** | `/loans` | Loan lifecycle & repayment schedules | 4 |
| **Risk** | `/borrowers/{id}/risk` | Risk scoring, affordability, alerts | 3 |
| **Simulation** | `/simulate` | Stress tests & what-if scenarios | 2 |

---

## 1. Borrowers

### `GET /borrowers`
List all borrowers with summary financial metrics.

**Response** `200 OK`:
```json
{
  "borrowers": [
    {
      "id": 1,
      "name": "Priya Sharma",
      "persona_type": "vendor",
      "location": "Mumbai Market District",
      "status": "active",
      "active_loans": 1,
      "risk_tier": "moderate",
      "affordability_score": 62.5,
      "avg_monthly_income": 945.00,
      "income_volatility_cv": 0.35
    }
  ],
  "total": 12,
  "at_risk_count": 3
}
```

### `GET /borrowers/{borrower_id}`
Full borrower profile with financial snapshot.

**Response** `200 OK`:
```json
{
  "id": 1,
  "name": "Priya Sharma",
  "persona_type": "vendor",
  "location": "Mumbai Market District",
  "registered_at": "2025-09-01",
  "status": "active",
  "financial_snapshot": {
    "avg_daily_inflow": 31.50,
    "avg_daily_burn": 22.80,
    "cash_buffer_days": 8.2,
    "inflow_cv": 0.35,
    "seasonality_ratio": 0.62,
    "current_balance": 284.50,
    "trend_direction": "stable",
    "zero_income_day_ratio": 0.04
  },
  "active_loans": [
    {
      "loan_id": 101,
      "principal": 500.00,
      "remaining_balance": 312.40,
      "schedule_type": "dynamic",
      "status": "active"
    }
  ]
}
```

### `GET /borrowers/{borrower_id}/summary`
Aggregated financial health summary with period comparisons.

---

## 2. Cash Flow

### `GET /borrowers/{borrower_id}/cashflow`
Raw transaction history with filtering.

**Query Parameters:**
| Param | Type | Default | Description |
|:------|:-----|:--------|:-----------|
| `start_date` | date | 90 days ago | Filter start |
| `end_date` | date | today | Filter end |
| `type` | string | all | `income`, `expense`, or `all` |
| `granularity` | string | `daily` | `daily`, `weekly`, or `monthly` |

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "period": { "start": "2025-06-15", "end": "2025-09-12" },
  "granularity": "daily",
  "data": [
    {
      "date": "2025-09-12",
      "total_inflow": 42.50,
      "total_outflow": -28.30,
      "net_cashflow": 14.20,
      "running_balance": 284.50,
      "transactions": [
        { "amount": 42.50, "type": "income", "category": "sales" },
        { "amount": -12.00, "type": "expense", "category": "inventory" },
        { "amount": -8.30, "type": "expense", "category": "food" },
        { "amount": -8.00, "type": "expense", "category": "fuel" }
      ]
    }
  ],
  "summary": {
    "total_inflow": 2835.00,
    "total_outflow": -2048.50,
    "net": 786.50,
    "avg_daily_net": 8.74
  }
}
```

### `GET /borrowers/{borrower_id}/cashflow/decomposition`
STL time-series decomposition of income stream.

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "period": 7,
  "decomposition": {
    "dates": ["2025-06-15", "2025-06-16", "..."],
    "observed": [28.5, 32.1, "..."],
    "trend": [30.2, 30.3, "..."],
    "seasonal": [-1.7, 1.8, "..."],
    "residual": [0.0, 0.0, "..."]
  },
  "insights": {
    "trend_direction": "slight_upward",
    "trend_slope_per_month": 2.15,
    "seasonal_amplitude": 12.40,
    "peak_day": "Saturday",
    "trough_day": "Monday",
    "peak_month": "November",
    "trough_month": "June"
  }
}
```

### `GET /borrowers/{borrower_id}/cashflow/forecast`
Forward-looking cash flow prediction with confidence bands.

**Query Parameters:**
| Param | Type | Default | Description |
|:------|:-----|:--------|:-----------|
| `horizon_days` | int | 30 | Forecast horizon (max 90) |

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "forecast_generated_at": "2025-09-12T18:30:00Z",
  "horizon_days": 30,
  "model_used": "quantile_lgbm",
  "forecast": [
    {
      "date": "2025-09-13",
      "p10": 18.20,
      "p50": 31.40,
      "p90": 48.60,
      "day_of_week": "Saturday",
      "seasonal_factor": 1.5
    }
  ],
  "monthly_summary": {
    "expected_total_inflow": 942.00,
    "conservative_total_inflow_p10": 546.00,
    "optimistic_total_inflow_p90": 1458.00
  }
}
```

---

## 3. Loans

### `POST /loans`
Create a new loan with dynamic repayment schedule.

**Request Body:**
```json
{
  "borrower_id": 1,
  "principal": 500.00,
  "annual_interest_rate": 0.18,
  "tenure_months": 6,
  "schedule_type": "dynamic"
}
```

**Response** `201 Created`:
```json
{
  "loan_id": 101,
  "borrower_id": 1,
  "principal": 500.00,
  "annual_interest_rate": 0.18,
  "base_emi": 88.26,
  "tenure_months": 6,
  "schedule_type": "dynamic",
  "disbursement_date": "2025-09-12",
  "dynamic_schedule": [
    {
      "period": 1,
      "due_date": "2025-10-12",
      "scheduled_amount": 72.40,
      "interest_component": 7.50,
      "principal_component": 64.90,
      "remaining_balance": 435.10,
      "adjustment_reason": "seasonal_low",
      "affordability_score_at_time": 58.3
    }
  ],
  "comparison_with_fixed": {
    "fixed_total_interest": 29.56,
    "dynamic_estimated_total_interest": 33.80,
    "dynamic_estimated_tenure_months": 7,
    "fixed_missed_payment_months": [3, 4],
    "dynamic_missed_payment_months": []
  }
}
```

### `GET /loans/{loan_id}`
Get loan details and current status.

### `GET /loans/{loan_id}/schedule`
Current dynamic repayment schedule with history of adjustments.

**Response** `200 OK`:
```json
{
  "loan_id": 101,
  "schedule_type": "dynamic",
  "base_emi": 88.26,
  "sweep_percentage": 0.20,
  "payment_floor": 44.13,
  "payment_cap": 132.39,
  "current_period": 3,
  "remaining_balance": 312.40,
  "original_tenure_months": 6,
  "adjusted_tenure_months": 7,
  "schedule": [
    {
      "period": 1,
      "due_date": "2025-10-12",
      "scheduled": 72.40,
      "actual_paid": 72.40,
      "status": "paid",
      "adjustment_reason": "standard",
      "das_at_time": 62.5
    },
    {
      "period": 2,
      "due_date": "2025-11-12",
      "scheduled": 105.80,
      "actual_paid": 105.80,
      "status": "paid",
      "adjustment_reason": "surplus_available",
      "das_at_time": 78.2
    },
    {
      "period": 3,
      "due_date": "2025-12-12",
      "scheduled": 48.50,
      "actual_paid": null,
      "status": "upcoming",
      "adjustment_reason": "seasonal_low",
      "das_at_time": 41.0
    }
  ]
}
```

### `GET /loans/{loan_id}/schedule/comparison`
Side-by-side Traditional EMI vs Dynamic FlowLend schedule.

**Response** `200 OK`:
```json
{
  "loan_id": 101,
  "comparison": {
    "months": [1, 2, 3, 4, 5, 6, 7],
    "traditional_emi": {
      "payments": [88.26, 88.26, 88.26, 88.26, 88.26, 88.26, null],
      "total_paid": 529.56,
      "total_interest": 29.56,
      "missed_payments": 2,
      "missed_months": [3, 4],
      "penalty_fees": 26.48,
      "effective_cost": 556.04
    },
    "dynamic_flowlend": {
      "payments": [72.40, 105.80, 48.50, 52.10, 95.20, 110.50, 38.90],
      "total_paid": 523.40,
      "total_interest": 23.40,
      "missed_payments": 0,
      "missed_months": [],
      "penalty_fees": 0,
      "effective_cost": 523.40
    },
    "monthly_cashflow": [850, 1120, 420, 480, 980, 1150, 380],
    "verdict": {
      "savings_for_borrower": 32.64,
      "defaults_prevented": 2,
      "tenure_extension_months": 1,
      "summary": "FlowLend prevented 2 defaults and saved the borrower $32.64 in penalties, at the cost of 1 extra month of tenure."
    }
  }
}
```

---

## 4. Risk & Affordability

### `GET /borrowers/{borrower_id}/risk`
Risk assessment with SHAP explanations.

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "assessment_date": "2025-09-12",
  "default_probability": 0.18,
  "risk_tier": "moderate",
  "affordability_score": 62.5,
  "financial_state": "stable",
  "shap_explanations": {
    "base_value": 0.22,
    "features": [
      {
        "name": "cash_buffer_days",
        "value": 8.2,
        "shap_value": -0.08,
        "direction": "reduces_risk",
        "explanation": "Healthy cash buffer of 8.2 days reduces default risk"
      },
      {
        "name": "inflow_cv",
        "value": 0.35,
        "shap_value": 0.05,
        "direction": "increases_risk",
        "explanation": "Moderate income volatility (CV=0.35) slightly increases risk"
      },
      {
        "name": "seasonality_ratio",
        "value": 0.62,
        "shap_value": 0.03,
        "direction": "increases_risk",
        "explanation": "Seasonal income variation (min/max=0.62) adds minor risk"
      },
      {
        "name": "expense_to_income_ratio",
        "value": 0.72,
        "shap_value": -0.02,
        "direction": "reduces_risk",
        "explanation": "Healthy expense ratio of 72% leaves room for loan service"
      },
      {
        "name": "trend_slope",
        "value": 0.05,
        "shap_value": -0.02,
        "direction": "reduces_risk",
        "explanation": "Slight upward income trend indicates business growth"
      }
    ]
  },
  "counterfactual_guidance": [
    "Maintain average daily balance above $250 for 30 days to reduce risk tier to 'low'",
    "Build cash buffer to 12+ days for maximum affordability score improvement"
  ]
}
```

### `GET /borrowers/{borrower_id}/affordability`
Dynamic Affordability Score breakdown.

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "das_score": 62.5,
  "das_tier": "moderate",
  "components": {
    "d_dscr": {
      "value": 1.38,
      "contribution": 0.32,
      "weight": 0.35,
      "detail": "Conservative inflow ($546/mo P10) covers proposed payment ($88/mo) with 1.38x coverage"
    },
    "buffer_health": {
      "value": 0.68,
      "contribution": 0.17,
      "weight": 0.25,
      "detail": "Current balance ($284) is 68% of required safety buffer ($418)"
    },
    "discretionary_flexibility": {
      "value": 0.28,
      "contribution": 0.06,
      "weight": 0.20,
      "detail": "28% of expenses are discretionary and compressible under stress"
    },
    "downside_stability": {
      "value": 0.65,
      "contribution": 0.07,
      "weight": 0.20,
      "detail": "Downside volatility index of 0.35 — moderate income stability"
    }
  },
  "max_safe_installment": 78.50,
  "recommended_installment": 65.00,
  "action": "Standard scheduled repayment at recommended level"
}
```

### `GET /borrowers/{borrower_id}/alerts`
Active early warning signals.

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "alerts": [
    {
      "type": "cusum_trigger",
      "severity": "warning",
      "detected_at": "2025-09-10",
      "message": "Income trend dropped below 2-sigma threshold for 5 consecutive days",
      "cusum_statistic": 12.4,
      "threshold": 10.0,
      "recommended_action": "Consider reducing next payment to interest-only floor"
    }
  ],
  "financial_state_probabilities": {
    "thriving": 0.05,
    "stable": 0.25,
    "stressed": 0.55,
    "deteriorating": 0.10,
    "recovering": 0.05
  }
}
```

---

## 5. Simulation

### `POST /simulate/stress-test`
Simulate a revenue shock and see how the dynamic schedule adapts.

**Request Body:**
```json
{
  "loan_id": 101,
  "shock_percentage": -0.40,
  "shock_duration_days": 14,
  "shock_start_date": "2025-09-15"
}
```

**Response** `200 OK`:
```json
{
  "loan_id": 101,
  "scenario": "Revenue shock of -40% for 14 days starting 2025-09-15",
  "original_schedule": {
    "next_payment": 72.40,
    "remaining_tenure_months": 4,
    "total_remaining_interest": 18.20
  },
  "stressed_schedule": {
    "next_payment": 44.13,
    "adjustment": "Reduced to interest-only floor",
    "remaining_tenure_months": 5,
    "total_remaining_interest": 22.80,
    "recovery_month": "2025-11-12"
  },
  "traditional_emi_outcome": {
    "next_payment": 88.26,
    "would_default": true,
    "penalty_fee": 13.24,
    "cascading_risk": "High — missed payment damages credit, increases cost of future borrowing"
  },
  "timeline": [
    {
      "date": "2025-10-12",
      "dynamic_payment": 44.13,
      "fixed_payment": 88.26,
      "available_cashflow": 52.00,
      "dynamic_status": "paid_floor",
      "fixed_status": "MISSED"
    },
    {
      "date": "2025-11-12",
      "dynamic_payment": 98.50,
      "fixed_payment": 88.26,
      "available_cashflow": 120.00,
      "dynamic_status": "catch_up",
      "fixed_status": "paid_with_penalty"
    }
  ]
}
```

### `POST /simulate/restructure`
Compare alternative repayment structures for a borrower.

**Request Body:**
```json
{
  "borrower_id": 1,
  "loan_principal": 500.00,
  "annual_interest_rate": 0.18,
  "structures_to_compare": ["fixed_emi", "dynamic_sweep", "seasonal_adjusted", "graduated"]
}
```

**Response** `200 OK`:
```json
{
  "borrower_id": 1,
  "structures": [
    {
      "type": "fixed_emi",
      "monthly_payment": "88.26 (constant)",
      "tenure_months": 6,
      "total_interest": 29.56,
      "predicted_missed_payments": 2,
      "predicted_penalties": 26.48,
      "effective_cost": 556.04,
      "borrower_stress_score": 72
    },
    {
      "type": "dynamic_sweep",
      "monthly_payment": "38.90 — 110.50 (variable)",
      "tenure_months": 7,
      "total_interest": 33.80,
      "predicted_missed_payments": 0,
      "predicted_penalties": 0,
      "effective_cost": 533.80,
      "borrower_stress_score": 28
    },
    {
      "type": "seasonal_adjusted",
      "monthly_payment": "22.00 — 145.00 (seasonal index)",
      "tenure_months": 6,
      "total_interest": 31.20,
      "predicted_missed_payments": 0,
      "predicted_penalties": 0,
      "effective_cost": 531.20,
      "borrower_stress_score": 22
    },
    {
      "type": "graduated",
      "monthly_payment": "45.00 → 130.00 (step-up)",
      "tenure_months": 6,
      "total_interest": 35.40,
      "predicted_missed_payments": 1,
      "predicted_penalties": 13.24,
      "effective_cost": 548.64,
      "borrower_stress_score": 48
    }
  ],
  "recommendation": {
    "best_for_borrower": "seasonal_adjusted",
    "best_for_lender": "dynamic_sweep",
    "balanced_recommendation": "dynamic_sweep",
    "reasoning": "Dynamic sweep eliminates all predicted defaults while adding only 1 month of tenure. Total lender cost is $4.24 more in interest but saves $26.48 in collection/penalty costs."
  }
}
```

---

## Error Responses

All endpoints follow consistent error formatting:

```json
{
  "detail": "Borrower with id 999 not found",
  "status_code": 404,
  "error_type": "not_found"
}
```

| Status | Meaning |
|:-------|:--------|
| `400` | Invalid request parameters |
| `404` | Resource not found |
| `422` | Validation error (Pydantic) |
| `500` | Internal server error |
