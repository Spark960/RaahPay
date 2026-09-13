# RaahPay — Dynamic Microloan Repayment & Cash-Flow Planning

> **Hackathon Theme**: SDG 8 — Decent Work and Economic Growth  
> **Core Insight**: Fixed repayment schedules break borrowers with irregular income. RaahPay dynamically adapts repayments to real cash-flow patterns, preventing unnecessary defaults while ensuring sustainable loan recovery.

## Problem Summary

Microfinance borrowers — street vendors, seasonal farmers, gig workers — earn income on wildly irregular schedules. A fixed \$150/month EMI works fine in peak months but triggers cascading defaults during lean periods, even when the borrower is fundamentally creditworthy. The result: punitive late fees, credit score damage, and borrowers turning to predatory loan sharks — all from a scheduling problem, not a solvency problem.

**RaahPay solves this** by building an intelligent system that:
1. **Decomposes** borrower cash flow into trend, seasonal, and shock components
2. **Forecasts** future cash availability with confidence intervals
3. **Dynamically schedules** repayments that flex with income (higher in peaks, lower in troughs)
4. **Detects** financial stress early — before a payment bounces
5. **Explains** every decision with transparent, human-readable reasoning

---

## User Review Required

> [!IMPORTANT]
> **Tech Stack Decision**: We're recommending **FastAPI (Python)** backend + **React/Vite/Tailwind/shadcn** frontend + **SQLite** database. This maximizes ML integration speed and demo polish. The alternative is a pure Streamlit app (faster to build but less impressive). **Please confirm.**

> [!IMPORTANT]
> **Scope Decision**: The full system has 7 algorithmic modules (see [architecture.md](file:///C:/Users/parsa/.gemini/antigravity/brain/977cc299-4944-4601-87ae-1855c09ffd89/architecture.md)). For hackathon time constraints, we recommend implementing **Tiers 1-2** (core engine + risk scoring) and mocking Tier 3 (HMM states, survival analysis). **Please confirm priority.**

> [!WARNING]
> **Data Strategy**: We will generate **synthetic data** simulating 3 borrower personas (street vendor, seasonal farmer, gig worker) with realistic income patterns, shocks, and expenses. No real financial data will be used.

## Open Questions

1. **Team Size & Skill Split**: How many team members, and what's the frontend/backend/ML split? This affects module assignment.
2. **Demo Duration**: How long is the hackathon demo? (5 min vs 10 min changes what we prioritize visually)
3. **Judging Criteria**: Is it weighted more toward technical depth, business viability, or UI polish?

---

## Proposed Changes

### Implementation Tiers (Priority Order)

| Tier | Components | Time Estimate | Impact |
|:-----|:-----------|:--------------|:-------|
| **Tier 1 — Core Engine** | Synthetic data generator, Cash-flow feature extraction, STL decomposition, Dynamic repayment scheduler | ~6-8 hours | The beating heart — without this, nothing works |
| **Tier 2 — Intelligence Layer** | Risk scoring (LightGBM + SHAP), Affordability scoring (DAS), Cash flow forecasting, Early warning system (CUSUM) | ~6-8 hours | Makes it smart — transforms raw data into decisions |
| **Tier 3 — Advanced Analytics** | HMM financial states, Change point detection (BOCPD), Survival analysis, Counterfactual explanations (DiCE) | ~4-6 hours | Differentiator — sets us apart from other teams |
| **Tier 4 — Frontend & Demo** | Lender dashboard, Borrower detail view, Interactive stress-test simulator, SHAP explanation cards | ~6-8 hours | Makes it sellable — judges see and believe |

---

### Component 1: Data Layer

#### [NEW] `backend/data/seed_synthetic.py`
Procedural generator for realistic microfinance transaction data. Three borrower personas:
- **Persona A** — *Street Food Vendor*: High weekend surge, low weekday baseline, rain-shock days
- **Persona B** — *Seasonal Maize Farmer*: Harvest peaks (Oct-Dec), lean hungry season (Feb-Apr)  
- **Persona C** — *Gig Delivery Rider*: Festival/event spikes, app-algorithm variability

Mathematical model per persona:
$$\text{Revenue}(t) = (\text{Base} + \text{Trend} \cdot t) \times S_{\text{weekly}}(t) \times S_{\text{seasonal}}(t) \times \xi_{\text{noise}} - \text{Shocks}(t)$$

#### [NEW] `backend/app/models/` (SQLModel schemas)
- `borrower.py` — Borrower profile, persona type, registration date
- `transaction.py` — Daily transactions (inflow/outflow, category, amount)
- `loan.py` — Loan terms, disbursement, status
- `repayment.py` — Scheduled vs actual payments, dynamic adjustments

#### [NEW] `backend/app/core/database.py`
SQLite + SQLModel connection. Zero-config, single-file DB.

---

### Component 2: Analytics Engine

#### [NEW] `backend/app/services/time_series.py`
- STL decomposition (statsmodels) → extracts trend, seasonal, residual
- Fourier-based seasonality detection for weekly/monthly/annual cycles
- Confidence interval generation for forecasts

#### [NEW] `backend/app/services/cashflow_features.py`
Feature extraction pipeline computing:
- Free Discretionary Cash Flow (FDCF)
- Debt Service Coverage Ratio (DSCR)  
- Cash Buffer Days
- Inflow Coefficient of Variation
- Seasonality Ratio (min month / max month)
- Balance Depletion Speed
- Zero-Cash Day Proportion

#### [NEW] `backend/app/services/dynamic_scheduler.py`
The core adaptive repayment engine:
$$\text{Installment}_t = \text{clip}\left(\alpha \cdot \text{NetInflow}_t \cdot S_t,\ I_{\min},\ I_{\max}\right)$$
- $\alpha = 0.20$ (sweep 20% of net discretionary inflow)
- $I_{\min}$ = interest-only floor (prevents negative amortization)
- $I_{\max} = 1.5 \times$ base EMI (prevents liquidity shock)
- Tenure dynamically expands/contracts based on payment velocity

#### [NEW] `backend/app/services/risk_engine.py`
- LightGBM classifier for default probability
- TreeSHAP explainer → top 3-5 adverse action reason codes
- Dynamic Affordability Score (DAS ∈ [0, 100]) composite metric
- CUSUM-based early warning system for financial distress detection

---

### Component 3: API Layer

#### [NEW] `backend/app/api/borrowers.py`
- `GET /borrowers` — List all borrowers with summary stats
- `GET /borrowers/{id}` — Full borrower profile + financial snapshot

#### [NEW] `backend/app/api/cashflow.py`
- `GET /borrowers/{id}/cashflow` — Raw transaction history
- `GET /borrowers/{id}/cashflow/decomposition` — STL trend/seasonal/residual
- `GET /borrowers/{id}/cashflow/forecast` — 30-90 day forecast with P10/P50/P90

#### [NEW] `backend/app/api/loans.py`
- `POST /loans` — Create loan with dynamic schedule
- `GET /loans/{id}/schedule` — Current dynamic repayment schedule
- `GET /loans/{id}/schedule/comparison` — Dynamic vs Traditional EMI comparison

#### [NEW] `backend/app/api/risk.py`
- `GET /borrowers/{id}/risk` — Risk score + SHAP explanations
- `GET /borrowers/{id}/affordability` — Dynamic Affordability Score
- `GET /borrowers/{id}/alerts` — Early warning signals

#### [NEW] `backend/app/api/simulation.py`
- `POST /simulate/stress-test` — "What-if" revenue shock simulator
- `POST /simulate/restructure` — Alternative repayment structure comparison

---

### Component 4: Frontend Dashboard

#### [NEW] `frontend/src/pages/Dashboard.tsx`
Portfolio overview for lenders:
- Total active loans, at-risk count, recovery rate
- Borrower cards with risk badges (Low/Medium/High/Critical)
- Alert feed for early warning triggers

#### [NEW] `frontend/src/pages/BorrowerDetail.tsx`
Deep-dive on individual borrower:
- Cash flow chart (observed + decomposed trend/seasonal)
- Dynamic repayment schedule visualization
- Side-by-side: "Traditional EMI" vs "RaahPay Dynamic" comparison
- Risk explanation card with SHAP waterfall

#### [NEW] `frontend/src/components/CashFlowChart.tsx`
Recharts area chart with gradient fills showing:
- Historical cash flow (solid line)
- Forecasted cash flow (dashed line with P10-P90 confidence band)
- Repayment overlay (bar chart showing scheduled payments)

#### [NEW] `frontend/src/components/StressTestSlider.tsx`
Interactive slider: "Simulate -X% revenue shock for N days"
- Real-time API call to recompute dynamic schedule
- Animated transition showing how RaahPay adapts vs fixed EMI defaults

#### [NEW] `frontend/src/components/RiskExplanationCard.tsx`
SHAP-powered explanation panel:
- Waterfall chart showing feature contributions to risk score
- Human-readable reason codes ("High cash flow volatility contributes +24% to risk")
- Counterfactual guidance ("To reduce risk: maintain \$250 avg daily balance for 30 days")

#### [NEW] `frontend/src/components/RepaymentComparison.tsx`
The "money shot" visualization:
- Dual-line chart: Traditional EMI (flat line) vs Dynamic schedule (wave)
- Highlight zones where traditional plan enters "Default/Penalty" territory
- Show how dynamic plan catches up during peak seasons

---

## Verification Plan

### Automated Tests
```bash
# Backend unit tests
cd backend && python -m pytest tests/ -v

# Synthetic data validation
python -m pytest tests/test_data_generator.py -v

# API integration tests  
python -m pytest tests/test_api.py -v

# ML model sanity checks
python -m pytest tests/test_risk_engine.py -v
```

### Manual Verification
1. **Data Quality**: Generate synthetic data for all 3 personas, visually inspect seasonality patterns
2. **Dynamic Scheduler**: Verify that payments reduce during simulated lean periods and increase during peaks
3. **No-Default Guarantee**: Run 12-month simulation — dynamic schedule should have 0 missed payments where fixed EMI has 3-4
4. **SHAP Explanations**: Verify that top risk factors are sensible and human-readable
5. **Stress Test**: Use the slider to inject a -50% shock and confirm the schedule adapts within 1 period
6. **End-to-End Demo**: Run the full flow from borrower data → risk assessment → dynamic schedule → lender dashboard
