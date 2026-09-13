# FlowLend — Frontend UI/UX Design

> Design system, wireframes, and component specifications for the lender dashboard.

---

## Design Philosophy

FlowLend's UI should feel like a **modern fintech analytics platform** — clean, data-dense, but not overwhelming. The target user is a **microfinance loan officer** who needs to:
1. Quickly assess portfolio health at a glance
2. Deep-dive into individual borrower cash flow patterns
3. Understand and trust AI-generated recommendations
4. Run interactive simulations before making decisions

---

## Design System

### Color Palette

| Role | Color | Hex | Usage |
|:-----|:------|:----|:------|
| **Primary** | Indigo | `#4F46E5` | Navigation, CTAs, active states |
| **Success** | Emerald | `#10B981` | Positive indicators, on-track payments |
| **Warning** | Amber | `#F59E0B` | Moderate risk, caution states |
| **Danger** | Rose | `#F43F5E` | High risk, missed payments, defaults |
| **Critical** | Red | `#DC2626` | Emergency alerts, system failures |
| **Neutral** | Slate | `#64748B` | Body text, secondary elements |
| **Background** | White/Slate-50 | `#FFFFFF` / `#F8FAFC` | Page background |
| **Surface** | White | `#FFFFFF` | Card backgrounds |
| **Forecast Band** | Indigo (10% opacity) | `#4F46E5/10` | P10-P90 confidence interval fill |

### Risk Tier Badge Colors

| Tier | Background | Text | Border |
|:-----|:-----------|:-----|:-------|
| 🟢 Low | `bg-emerald-50` | `text-emerald-700` | `border-emerald-200` |
| 🟡 Moderate | `bg-amber-50` | `text-amber-700` | `border-amber-200` |
| 🟠 High | `bg-orange-50` | `text-orange-700` | `border-orange-200` |
| 🔴 Critical | `bg-rose-50` | `text-rose-700` | `border-rose-200` |

### Typography

| Element | Font | Size | Weight |
|:--------|:-----|:-----|:-------|
| Page Title | Inter | 24px | 700 (Bold) |
| Section Header | Inter | 18px | 600 (Semibold) |
| Card Title | Inter | 14px | 600 (Semibold) |
| Body | Inter | 14px | 400 (Regular) |
| Metric Value | Inter | 28px | 700 (Bold) |
| Metric Label | Inter | 12px | 500 (Medium) |
| Code/Data | JetBrains Mono | 13px | 400 (Regular) |

---

## Page 1: Portfolio Dashboard

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  🏦 FlowLend          [Dashboard] [Simulator]    🔔 👤  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Total    │ │ Active   │ │ At-Risk  │ │ Recovery │   │
│  │ Loans    │ │ Loans    │ │ Loans    │ │ Rate     │   │
│  │   12     │ │    8     │ │    3     │ │  97.2%   │   │
│  │ ▲ +2 mo  │ │          │ │ ⚠ +1     │ │ ▲ +2.1pp │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                         │
│  ┌─────────────────────────────────┐ ┌───────────────┐  │
│  │ Borrower Portfolio Table        │ │ Alert Feed    │  │
│  │ ┌────┬────────┬──────┬────────┐ │ │               │  │
│  │ │Name│Persona │Risk  │DAS    ││ │ │ ⚠ Kofi: CUSUM │  │
│  │ ├────┼────────┼──────┼────────┤ │ │   trigger     │  │
│  │ │Priy│Vendor  │🟡 Mod│62.5   ││ │ │               │  │
│  │ │Kofi│Farmer  │🟠 Hi │38.0   ││ │ │ ℹ Amara:      │  │
│  │ │Amar│Gig     │🟢 Low│78.2   ││ │ │   surplus     │  │
│  │ └────┴────────┴──────┴────────┘ │ │   detected    │  │
│  │                    [View All →]  │ │               │  │
│  └─────────────────────────────────┘ └───────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Portfolio Risk Distribution          (Pie Chart) │   │
│  │   🟢 Low: 5  🟡 Moderate: 4  🟠 High: 2  🔴: 1 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### KPI Cards Specification
- **Size**: 4 equal-width cards in a responsive grid (4-col on desktop, 2-col on tablet, 1-col on mobile)
- **Content**: Large metric value (28px bold), label below (12px medium), trend indicator with color
- **Hover**: Subtle shadow elevation + tooltip with period comparison

### Borrower Table
- **Columns**: Name, Persona Type, Location, Risk Tier (badge), DAS Score (colored bar), Active Loan, Last Payment Status
- **Sortable**: Click column headers to sort
- **Clickable rows**: Navigate to Borrower Detail
- **Search/Filter**: Filter by risk tier, persona, status

### Alert Feed
- **Real-time** style card list (most recent first)
- **Color-coded** by severity (info/warning/danger)
- **Actionable**: Click to navigate to relevant borrower

---

## Page 2: Borrower Detail View

### Layout (Tabbed)

```
┌─────────────────────────────────────────────────────────┐
│  ← Back to Portfolio                                    │
│                                                         │
│  ┌───────────────────────────┐ ┌──────────────────────┐ │
│  │ 👤 Kofi Mensah            │ │ Risk Assessment      │ │
│  │ Seasonal Maize Farmer     │ │ ┌──────┐             │ │
│  │ 📍 Tamale, Ghana          │ │ │ 18%  │ P(Default)  │ │
│  │ Since: Sep 2025           │ │ │ 🟠   │ Moderate    │ │
│  │                           │ │ └──────┘             │ │
│  │ Avg Monthly: $420         │ │ DAS: ████░░░  38.0   │ │
│  │ Volatility: CV=0.70      │ │ State: 🟡 Stressed   │ │
│  └───────────────────────────┘ └──────────────────────┘ │
│                                                         │
│  [Cash Flow] [Repayment] [Risk & SHAP] [Stress Test]   │
│  ─────────────────────────────────────────────────────   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │                                                  │   │
│  │          << TAB CONTENT AREA >>                  │   │
│  │                                                  │   │
│  │  (See component specifications below)            │   │
│  │                                                  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Key Component Specifications

### 1. Cash Flow Chart (`CashFlowChart.tsx`)

**Type**: Recharts `ComposedChart` — Area + Line + Bar

```
Revenue ($)
    ^
120 |                    ╱╲
    |        ╱╲         ╱  ╲        ╱╲
 80 |  ╱╲  ╱  ╲       ╱    ╲      ╱  ╲
    | ╱  ╲╱    ╲  ╱╲ ╱      ╲    ╱    ╲
 40 |╱         ╲╱  ╲╱        ╲──╱      ╲
    |                                    ╲
  0 ├──────────────────┼─────────────────────→ Time
    │   Historical     │    Forecast (30d)
    │   (solid line)   │    (dashed + band)
    │                  │
    │   ████ ████ ████ │ ░░░░ ░░░░ ░░░░   ← Repayment bars
    │   (green=paid)   │ (blue=scheduled)
```

**Layers** (bottom to top):
1. **P10-P90 Confidence Band**: Soft indigo gradient fill (10% opacity)
2. **Historical Income**: Solid emerald line with dot markers
3. **Forecasted Income (P50)**: Dashed indigo line
4. **Repayment Bars**: Semi-transparent bars overlaid on the timeline
5. **Fixed EMI Reference Line**: Thin red dashed horizontal line (for comparison)

**Interactivity**:
- Hover tooltip showing exact values for all layers
- Click a data point to see that day's transactions
- Toggle layers on/off via legend

### 2. STL Decomposition View (`SeasonalityView.tsx`)

**Type**: 4 vertically stacked synchronized Recharts `LineChart`

```
Observed   ─── (original data, gray)
Trend      ─── (smooth growth line, blue)
Seasonal   ─── (repeating wave, orange)
Residual   ─── (noise/shocks, gray dots)
```

Each chart shares the same x-axis (time), allowing visual alignment.

### 3. SHAP Waterfall Chart (`ShapWaterfall.tsx`)

**Type**: Custom horizontal bar chart (Recharts `BarChart` or custom SVG)

```
Base Risk Score (22%)  ──────────────────────┐
                                              │
  cash_buffer_days       ████████ (-8%)      │
  seasonality_ratio      ███ (+3%)            │
  inflow_cv              █████ (+5%)          │
  expense_ratio          ██ (-2%)             │
  trend_slope            ██ (-2%)             │
                                              │
Final Risk Score (18%)  ──────────────────────┘
```

**Design**:
- Green bars = risk-reducing features (extending left)
- Red bars = risk-increasing features (extending right)
- Each bar labeled with feature name + human-readable explanation
- Base value and final value shown at top and bottom

### 4. Repayment Comparison (`RepaymentComparison.tsx`)

**Type**: Recharts `ComposedChart` — Dual Line + Shaded Zones

```
Payment ($)
    ^
140 |                  ╱╲           ╱╲
    |                 ╱  ╲         ╱  ╲
100 |─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  Fixed EMI ($88)
    |        ╱╲     ╱    ╲       ╱    ╲
 60 |  ╱╲  ╱  ╲   ╱      ╲     ╱      ╲
    | ╱  ╲╱    ╲─╱        ╲───╱        ╲
 40 |╱                                   ╲   Dynamic
    |                                      
  0 ├───┬───┬───┬───┬───┬───┬───┬───────→ Month
    1   2   3   4   5   6   7

    ░░░░░░░░ DEFAULT ZONE ░░░░░░░░  ← Red shading where
         (months 3-4, fixed EMI)      income < fixed payment
```

**Critical Design Elements**:
- **Red shaded zones**: Where income drops below fixed EMI → default territory
- **Green dynamic line**: The FlowLend adaptive schedule
- **Dashed red line**: Fixed EMI reference
- **Gray area**: Monthly income/cash flow background
- **Annotations**: Labels on key months ("Lean season", "Harvest peak", "Catch-up")

### 5. Stress Test Slider (`StressTestSlider.tsx`)

**Design**: Full-width interactive panel

```
┌──────────────────────────────────────────────────────┐
│  🔬 Revenue Stress Test Simulator                    │
│                                                      │
│  Shock Magnitude:  ──●──────────────  -40%          │
│                    -10%            -90%               │
│                                                      │
│  Shock Duration:   ──────●──────────  14 days        │
│                    7d              60d                │
│                                                      │
│  [Run Simulation]                                    │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  << ANIMATED CHART SHOWING RESULT >>           │  │
│  │                                                │  │
│  │  Next Payment: $88 → $44 (interest-only)      │  │
│  │  Tenure: 6mo → 7mo (+1 month)                 │  │
│  │  Defaults: 2 (fixed) → 0 (dynamic)            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────┐ ┌──────────────┐                   │
│  │ Fixed EMI    │ │ FlowLend     │                   │
│  │ ❌ 2 defaults│ │ ✅ 0 defaults │                   │
│  │ $26 penalty  │ │ $0 penalty   │                   │
│  └──────────────┘ └──────────────┘                   │
└──────────────────────────────────────────────────────┘
```

**Behavior**:
- Slider drag fires debounced API call (300ms)
- Chart smoothly animates (CSS transition or Recharts animation)
- Result cards update with fade-in transition
- Comparison cards use green/red coloring for instant visual feedback

### 6. Risk Score Gauge (`RiskScoreGauge.tsx`)

**Type**: Circular SVG gauge (like a speedometer)

```
         ╭───────────╮
       ╱  🟢  🟡  🟠  🔴 ╲
      ╱                     ╲
     │                       │
     │        18%             │
     │     Moderate           │
      ╲                     ╱
       ╲                   ╱
         ╰───────────╯
```

**Zones**: 0-15% (Green/Low), 15-30% (Yellow/Moderate), 30-50% (Orange/High), 50%+ (Red/Critical)

**Needle animation**: Smooth CSS transition on value change.

---

## Animation Specifications

| Element | Trigger | Animation | Duration |
|:--------|:--------|:----------|:---------|
| Chart data update | API response | Recharts built-in morph | 500ms |
| Stress test result | Slider change | Fade-in + slide-up | 300ms |
| Risk gauge needle | Score change | CSS transform rotate | 800ms ease-out |
| KPI card trend | Page load | Count-up number | 600ms |
| Alert feed item | New alert | Slide-in from right | 400ms |
| Tab content | Tab switch | Fade crossfade | 200ms |

---

## Responsive Breakpoints

| Breakpoint | Width | Layout Adjustments |
|:-----------|:------|:------------------|
| Desktop | ≥1280px | Full layout as designed |
| Tablet | 768–1279px | KPI cards → 2-col grid, table columns reduce |
| Mobile | <768px | Single column, charts stack vertically |

> [!TIP]
> For the hackathon demo, optimize for **1920×1080 full-screen presentation**. Mobile responsiveness is nice-to-have but not critical for judging.
