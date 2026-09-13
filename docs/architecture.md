# FlowLend — System Architecture

> Complete technical architecture for the Dynamic Microloan Repayment & Cash-Flow Planning system.

---

## High-Level System Architecture

```mermaid
flowchart TB
    subgraph DataLayer["🗄️ Data Layer"]
        SIM["Synthetic Data Generator<br/>3 Personas × 12mo history"]
        DB[("SQLite Database<br/>SQLModel ORM")]
        SIM --> DB
    end

    subgraph AnalyticsEngine["🧠 Analytics Engine (Python)"]
        direction TB
        FE["Feature Extraction<br/>Cash Flow Metrics"]
        STL["STL Decomposition<br/>Trend / Seasonal / Residual"]
        FORECAST["Cash Flow Forecaster<br/>Quantile GBDT / ETS"]
        RISK["Risk Scorer<br/>LightGBM + TreeSHAP"]
        DAS["Affordability Scorer<br/>Dynamic DAS ∈ [0,100]"]
        EWS["Early Warning System<br/>CUSUM Anomaly Detection"]
        SCHED["Dynamic Repayment<br/>Scheduler (Bounded Sweep)"]
        
        FE --> STL
        STL --> FORECAST
        FE --> RISK
        FORECAST --> DAS
        RISK --> DAS
        DAS --> SCHED
        FE --> EWS
        EWS -.->|"Stress Alert"| SCHED
    end

    subgraph API["⚡ FastAPI Backend"]
        direction TB
        EP_B["/borrowers"]
        EP_CF["/cashflow"]
        EP_L["/loans"]
        EP_R["/risk"]
        EP_S["/simulate"]
    end

    subgraph Frontend["🖥️ React + Vite Dashboard"]
        direction TB
        DASH["Portfolio Dashboard"]
        DETAIL["Borrower Detail View"]
        CHART["Cash Flow Chart<br/>Recharts"]
        STRESS["Stress Test Simulator<br/>Interactive Sliders"]
        SHAP_UI["SHAP Explanation Cards"]
        COMPARE["EMI vs Dynamic<br/>Comparison View"]
    end

    DB --> FE
    AnalyticsEngine --> API
    API <--> Frontend
```

---

## Data Flow Pipeline

```mermaid
sequenceDiagram
    participant Gen as Data Generator
    participant DB as SQLite
    participant FE as Feature Engine
    participant ML as ML Pipeline
    participant Sched as Dynamic Scheduler
    participant API as FastAPI
    participant UI as React Dashboard

    Gen->>DB: Seed borrower profiles + 12mo transactions
    
    Note over FE: On-demand computation
    API->>DB: Fetch borrower transactions
    DB-->>FE: Raw transaction stream
    FE->>FE: Extract 15+ cash flow features
    FE->>ML: Feature vector
    
    par Risk Scoring
        ML->>ML: LightGBM predict P(default)
        ML->>ML: TreeSHAP explanations
    and Cash Flow Forecast
        FE->>FE: STL decomposition
        FE->>FE: Quantile forecast (P10, P50, P90)
    and Affordability
        ML->>ML: Compute DAS composite score
    end
    
    ML->>Sched: Risk score + DAS + Forecast
    Sched->>Sched: Optimize payment vector p_t*
    Sched-->>API: Dynamic schedule + comparison
    API-->>UI: JSON response
    UI->>UI: Render interactive dashboard
    
    Note over UI: User triggers stress test
    UI->>API: POST /simulate/stress-test {shock: -40%, duration: 14d}
    API->>Sched: Recompute with shocked forecast
    Sched-->>API: Adapted schedule
    API-->>UI: Animated re-render
```

---

## Database Schema

```mermaid
erDiagram
    BORROWER {
        int id PK
        string name
        string persona_type "vendor | farmer | gig_worker"
        float base_monthly_income
        string location
        date registered_at
        string status "active | defaulted | completed"
    }
    
    TRANSACTION {
        int id PK
        int borrower_id FK
        date transaction_date
        float amount "positive=inflow, negative=outflow"
        string type "income | expense | transfer"
        string category "sales | wages | rent | food | inventory | utilities | other"
        string description
    }
    
    LOAN {
        int id PK
        int borrower_id FK
        float principal
        float annual_interest_rate
        int original_tenure_months
        int adjusted_tenure_months
        float base_emi
        date disbursement_date
        string status "active | completed | defaulted | restructured"
        string schedule_type "dynamic | fixed"
    }
    
    REPAYMENT {
        int id PK
        int loan_id FK
        int period_number
        date due_date
        float scheduled_amount
        float actual_amount
        float principal_component
        float interest_component
        float remaining_balance
        string status "paid | partial | missed | deferred"
        string adjustment_reason "seasonal_low | stress_detected | surplus_available | standard"
    }
    
    RISK_ASSESSMENT {
        int id PK
        int borrower_id FK
        date assessment_date
        float default_probability
        float affordability_score "DAS 0-100"
        string risk_tier "low | moderate | high | critical"
        json shap_explanations
        json early_warnings
        string financial_state "thriving | stable | stressed | deteriorating | recovering"
    }
    
    BORROWER ||--o{ TRANSACTION : "generates"
    BORROWER ||--o{ LOAN : "holds"
    BORROWER ||--o{ RISK_ASSESSMENT : "assessed_by"
    LOAN ||--o{ REPAYMENT : "scheduled_in"
```

---

## Analytical Pipeline — 7-Module Architecture

The analytics engine processes raw transaction data through a layered pipeline where each module's output feeds downstream consumers:

```mermaid
flowchart LR
    subgraph Input
        TX["Raw Transactions<br/>date, amount, category"]
    end
    
    subgraph Tier1["Tier 1: Foundation"]
        M1["①  STL Decomposition<br/>Trend + Seasonal + Residual"]
        M2["②  Cash Flow Forecast<br/>P10 / P50 / P90 bands"]
    end
    
    subgraph Tier2["Tier 2: Intelligence"]
        M3["③  Affordability Score<br/>DAS ∈ [0, 100]"]
        M4["④  Risk Scorer<br/>LightGBM + SHAP"]
        M5["⑤  Early Warning<br/>CUSUM Detector"]
    end
    
    subgraph Tier3["Tier 3: Advanced"]
        M6["⑥  Financial State HMM<br/>5-state latent model"]
        M7["⑦  Change Point Detection<br/>BOCPD / PELT"]
    end
    
    subgraph Output
        SCHED["Dynamic Repayment<br/>Schedule p_t*"]
    end
    
    TX --> M1 --> M2
    TX --> M4
    TX --> M5
    TX --> M6
    TX --> M7
    
    M2 --> M3
    M4 --> M3
    M6 --> M3
    
    M3 --> SCHED
    M2 --> SCHED
    M5 -.->|"Alert"| SCHED
    M7 -.->|"Reset"| M2
```

### Module Interaction Matrix

| Module | Primary Input | Mechanism | Primary Output | Consumers |
|:-------|:-------------|:----------|:--------------|:----------|
| **① STL Decomposition** | Daily income series | Loess regression (seasonal + trend) | Trend $T_t$, Seasonal $S_t$, Residual $R_t$ | ② Forecaster |
| **② Cash Flow Forecast** | $T_t, S_t$, lag features | Quantile LightGBM or Holt-Winters ETS | $\hat{C}_t^{P_{10}}, \hat{C}_t^{P_{50}}, \hat{C}_t^{P_{90}}$ | ③ Affordability, ④ Scheduler |
| **③ Affordability Score** | Forecast, risk score, HMM state | D-DSCR + buffer health + volatility composite | $DAS_t \in [0, 100]$ | Scheduler, Dashboard |
| **④ Risk Scorer** | 15+ engineered features | LightGBM + TreeSHAP | $P(\text{default})$, reason codes | ③ Affordability, Dashboard |
| **⑤ Early Warning** | Daily balance stream | CUSUM statistic $S_t > h$ | Binary stress alert | Scheduler (triggers reduction) |
| **⑥ HMM States** | Multi-dim observation vector | Forward-Backward, Gaussian emissions | $P(Z_t = S_k)$ for 5 states | ③ Affordability, Policy rules |
| **⑦ Change Point Detection** | Income/balance series | BOCPD run-length posterior | Changepoint alarm $\tau$ | ② Forecast (resets training window) |

---

## Component Architecture — Backend

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory, CORS, lifespan
│   │
│   ├── core/
│   │   ├── config.py              # Settings (DB path, model params, sweep %)
│   │   └── database.py            # SQLite engine, session factory
│   │
│   ├── models/                    # SQLModel table definitions
│   │   ├── borrower.py
│   │   ├── transaction.py
│   │   ├── loan.py
│   │   ├── repayment.py
│   │   └── risk_assessment.py
│   │
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── borrower.py
│   │   ├── cashflow.py
│   │   ├── loan.py
│   │   ├── risk.py
│   │   └── simulation.py
│   │
│   ├── services/                  # Business logic & ML
│   │   ├── cashflow_features.py   # Feature extraction pipeline
│   │   ├── time_series.py         # STL decomposition + forecasting
│   │   ├── risk_engine.py         # LightGBM + SHAP + DAS
│   │   ├── dynamic_scheduler.py   # Bounded sweep repayment engine
│   │   ├── early_warning.py       # CUSUM anomaly detector
│   │   └── simulation.py          # Stress test & what-if engine
│   │
│   └── api/                       # Route handlers
│       ├── borrowers.py
│       ├── cashflow.py
│       ├── loans.py
│       ├── risk.py
│       └── simulation.py
│
├── data/
│   ├── seed_synthetic.py          # Persona-based data generator
│   └── demo.db                    # Pre-seeded demo database
│
├── tests/
│   ├── test_data_generator.py
│   ├── test_cashflow_features.py
│   ├── test_dynamic_scheduler.py
│   ├── test_risk_engine.py
│   └── test_api.py
│
└── requirements.txt
```

---

## Component Architecture — Frontend

```
frontend/
├── src/
│   ├── App.tsx                    # Router + layout
│   ├── main.tsx                   # Entry point
│   │
│   ├── components/
│   │   ├── ui/                    # shadcn/ui primitives
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── slider.tsx
│   │   │   ├── table.tsx
│   │   │   └── ...
│   │   │
│   │   ├── dashboard/
│   │   │   ├── PortfolioMetrics.tsx    # KPI cards (total loans, at-risk, etc.)
│   │   │   ├── BorrowerTable.tsx      # Sortable table with risk badges
│   │   │   └── AlertFeed.tsx          # Real-time early warning alerts
│   │   │
│   │   ├── borrower/
│   │   │   ├── CashFlowChart.tsx      # Recharts area + forecast bands
│   │   │   ├── SeasonalityView.tsx    # STL decomposition visualization
│   │   │   ├── RepaymentTimeline.tsx  # Payment history with status colors
│   │   │   └── FinancialStateCard.tsx # HMM state indicator
│   │   │
│   │   ├── risk/
│   │   │   ├── RiskScoreGauge.tsx     # Circular gauge (0-100)
│   │   │   ├── ShapWaterfall.tsx      # SHAP feature contribution chart
│   │   │   └── AffordabilityMeter.tsx # DAS score with zone coloring
│   │   │
│   │   └── simulation/
│   │       ├── StressTestSlider.tsx   # Revenue shock simulator
│   │       ├── RepaymentComparison.tsx # Dynamic vs Fixed EMI overlay
│   │       └── WhatIfPanel.tsx        # Restructuring options explorer
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx              # Portfolio overview page
│   │   ├── BorrowerDetail.tsx         # Individual borrower deep-dive
│   │   └── LoanSimulator.tsx          # New loan structuring tool
│   │
│   ├── services/
│   │   └── api.ts                     # Axios client for FastAPI
│   │
│   ├── hooks/
│   │   ├── useBorrower.ts
│   │   ├── useCashFlow.ts
│   │   └── useSimulation.ts
│   │
│   └── lib/
│       └── utils.ts                   # Formatting, color mapping
│
├── tailwind.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Tech Stack Summary

| Layer | Technology | Justification |
|:------|:-----------|:-------------|
| **Backend Framework** | FastAPI (Python 3.11+) | Auto Swagger docs, Pydantic validation, async, seamless ML integration |
| **Database** | SQLite + SQLModel | Zero config, single-file portable, SQLModel schemas = Pydantic models |
| **ML / Analytics** | scikit-learn, LightGBM, statsmodels, SHAP, NumPy, Pandas | Industry-standard ML stack, fast training, explainable |
| **Data Generation** | NumPy (Gamma/LogNormal) + Faker | Procedural generation of realistic non-linear cash flows |
| **Frontend** | React 18 + Vite + TypeScript | Fast HMR, full interactivity for sliders/simulations |
| **UI Components** | shadcn/ui + Tailwind CSS | Enterprise-grade fintech aesthetic in minutes |
| **Charts** | Recharts | Clean SVG charts, gradient fills, responsive, React-native |
| **HTTP Client** | Axios | Typed API calls with interceptors |

---

## Deployment Topology (Hackathon Demo)

```mermaid
flowchart LR
    subgraph LocalMachine["💻 Local Machine"]
        subgraph BackendProcess["Backend (Port 8000)"]
            UVICORN["uvicorn app.main:app"]
            SQLITE[("demo.db")]
            UVICORN <--> SQLITE
        end
        
        subgraph FrontendProcess["Frontend (Port 5173)"]
            VITE["vite dev server"]
        end
        
        VITE -->|"fetch /api/*"| UVICORN
    end
    
    BROWSER["🌐 Browser"] --> VITE
```

**Startup Commands:**
```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python data/seed_synthetic.py        # Generate demo data
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
```
