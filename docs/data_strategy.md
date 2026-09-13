# FlowLend — Data Strategy & Synthetic Generation

> How we create realistic, demo-ready financial data for 3 distinct borrower personas.

---

## Why Synthetic Data?

Real microfinance transaction data is:
- **Highly regulated** (PII, financial data protection laws)
- **Not publicly available** at the granularity we need (daily transactions)
- **Biased** toward formal banking customers, not our target population

Our synthetic generator creates **economically realistic** transaction streams that exhibit:
- ✅ Weekly market-day patterns (vendors)
- ✅ Annual harvest seasonality (farmers)
- ✅ Event-driven demand spikes (gig workers)
- ✅ Stochastic income shocks (illness, weather, equipment failure)
- ✅ Non-Gaussian distributions (Gamma/LogNormal for positive revenue skew)
- ✅ Realistic expense patterns with essential vs discretionary categories

---

## The Three Personas

### Persona A: Street Food Vendor — "Priya"

| Attribute | Value |
|:----------|:------|
| **Location** | Urban market district |
| **Base Daily Income** | \$25–40 |
| **Income Pattern** | Strong weekend surge (Fri-Sun), low Monday-Wednesday |
| **Volatility** | Moderate (CV ≈ 0.35) |
| **Shocks** | Rain days (zero revenue), minor health events |
| **Expenses** | Daily ingredient purchase, monthly rent, utilities |
| **Loan Purpose** | Cart upgrade, inventory expansion |

**Weekly Multiplier Pattern:**

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.6 | 0.7 | 0.8 | 0.9 | 1.3 | 1.5 | 1.2 |

**Monthly Seasonal Index** (relative to average):
Relatively flat with minor festival bumps.

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.9 | 0.9 | 1.0 | 1.0 | 1.0 | 0.8 | 0.8 | 0.9 | 1.0 | 1.1 | 1.3 | 1.2 |

---

### Persona B: Seasonal Maize Farmer — "Kofi"

| Attribute | Value |
|:----------|:------|
| **Location** | Rural agricultural zone |
| **Base Monthly Income** | \$50–200 (extreme seasonality) |
| **Income Pattern** | Harvest peak Oct-Dec, lean hungry season Feb-Apr |
| **Volatility** | Very high (CV ≈ 0.70) |
| **Shocks** | Drought, pest damage, crop price crashes |
| **Expenses** | Seed/fertilizer (pre-season bulk), minimal daily |
| **Loan Purpose** | Inputs for next planting season |

**Monthly Seasonal Index:**

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.4 | 0.2 | 0.2 | 0.3 | 0.5 | 0.6 | 0.7 | 0.8 | 1.0 | 1.8 | 2.0 | 1.5 |

> [!IMPORTANT]
> This is the most challenging persona for traditional fixed EMI. During Feb-Apr, income drops to 20% of annual average — a fixed \$100/month payment would consume 100%+ of income.

**Weekly Pattern:** Minimal (farming doesn't follow weekday/weekend patterns)

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.5 | 0.5 |

---

### Persona C: Gig Delivery Rider — "Amara"

| Attribute | Value |
|:----------|:------|
| **Location** | Peri-urban, app-based delivery |
| **Base Daily Income** | \$15–30 |
| **Income Pattern** | Event/festival spikes, app algorithm variability |
| **Volatility** | High (CV ≈ 0.50) |
| **Shocks** | Vehicle breakdown, app deactivation, fuel price spikes |
| **Expenses** | Daily fuel, weekly vehicle maintenance, phone data plan |
| **Loan Purpose** | Motorcycle purchase, phone upgrade |

**Weekly Multiplier:**

| Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.8 | 0.9 | 1.0 | 1.0 | 1.4 | 1.5 | 1.4 |

**Monthly Seasonal Index:**

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0.8 | 0.9 | 1.0 | 1.0 | 1.0 | 0.9 | 0.9 | 1.0 | 1.1 | 1.2 | 1.4 | 1.5 |

---

## Mathematical Revenue Model

For each borrower on each day $t$:

$$\text{Revenue}(t) = \max\!\left(0,\ (\text{Base} + \text{Trend} \cdot t) \times S_{\text{weekly}}(t) \times S_{\text{monthly}}(t) \times \xi_{\text{noise}} - \text{Shock}(t)\right)$$

### Component Definitions

| Component | Distribution / Formula | Parameters |
|:----------|:----------------------|:-----------|
| **Base** | Constant per persona | Vendor: \$30, Farmer: \$4/day, Gig: \$22 |
| **Trend** | Linear drift | \$0.02–0.05 per day (mild growth) |
| **$S_{\text{weekly}}(t)$** | Lookup table by day-of-week | See persona tables above |
| **$S_{\text{monthly}}(t)$** | Lookup table by month | See persona tables above |
| **$\xi_{\text{noise}}$** | $\sim \text{Gamma}(\alpha=5, \beta=5)$ | Mean = 1.0, right-skewed positive noise |
| **$\text{Shock}(t)$** | $\sim \text{Bernoulli}(p) \times \text{Uniform}(0.6, 0.95) \times \text{Revenue}$ | $p = 0.03$ (3% daily shock probability) |

### Shock Event Types

| Shock | Probability | Duration | Revenue Impact |
|:------|:-----------|:---------|:--------------|
| **Rain/Weather** | 3%/day | 1 day | -60% to -90% |
| **Minor Illness** | 1%/day | 2-5 days | -100% (zero income) |
| **Equipment Failure** | 0.5%/day | 3-7 days | -80% to -100% |
| **Market Disruption** | 0.2%/day | 5-14 days | -40% to -60% |
| **Major Health Event** | 0.1%/day | 14-30 days | -100% + medical expenses |

---

## Expense Model

### Essential Expenses (Non-Discretionary)

| Category | Frequency | Amount Model | Persona |
|:---------|:----------|:-------------|:--------|
| **Rent** | Monthly | Fixed: \$50–150 | All |
| **Utilities** | Monthly | Fixed: \$15–30 | All |
| **Basic Food** | Daily | Fixed: \$3–8 | All |
| **Raw Inventory** | Daily | 40% of previous day's revenue | Vendor |
| **Seeds/Fertilizer** | Seasonal (Mar, Aug) | \$100–300 bulk | Farmer |
| **Fuel** | Daily | \$4–8 | Gig Rider |
| **Phone/Data** | Monthly | \$10–20 | Gig Rider |

### Discretionary Expenses (Compressible)

| Category | Frequency | Amount Model |
|:---------|:----------|:-------------|
| **Entertainment** | Weekly | $\sim \text{Uniform}(\$5, \$20)$ |
| **Non-essential Shopping** | Bi-weekly | $\sim \text{LogNormal}(\mu=2.5, \sigma=0.5)$ |
| **Social Events** | Monthly | $\sim \text{Uniform}(\$10, \$50)$ |

---

## Generator Pseudocode

```python
def generate_borrower_data(persona: str, months: int = 12, seed: int = 42):
    """Generate daily transaction history for a borrower persona."""
    np.random.seed(seed)
    
    config = PERSONA_CONFIGS[persona]  # Base, trend, weekly/monthly patterns
    
    transactions = []
    start_date = datetime.now() - timedelta(days=months * 30)
    
    # Active shock state tracking
    shock_remaining_days = 0
    shock_severity = 0.0
    
    for day in range(months * 30):
        date = start_date + timedelta(days=day)
        dow = date.weekday()       # 0=Mon, 6=Sun
        month = date.month         # 1-12
        
        # === INCOME ===
        base = config.base_income + config.trend * day
        weekly_mult = config.weekly_pattern[dow]
        monthly_mult = config.monthly_pattern[month - 1]
        noise = np.random.gamma(5, 1/5)  # Mean=1, right-skewed
        
        daily_revenue = base * weekly_mult * monthly_mult * noise
        
        # Apply active shock
        if shock_remaining_days > 0:
            daily_revenue *= (1 - shock_severity)
            shock_remaining_days -= 1
        
        # Roll for new shock
        if shock_remaining_days == 0 and np.random.random() < 0.03:
            shock_type = np.random.choice(['weather', 'illness', 'equipment'])
            shock_severity = np.random.uniform(0.6, 0.95)
            shock_remaining_days = {'weather': 1, 'illness': 3, 'equipment': 5}[shock_type]
        
        # Record income transaction
        if daily_revenue > 0.50:  # Minimum transaction threshold
            transactions.append({
                'date': date, 'amount': round(daily_revenue, 2),
                'type': 'income', 'category': 'sales',
                'description': f'Daily {persona} revenue'
            })
        
        # === EXPENSES ===
        # Essential daily expenses
        food = np.random.uniform(config.food_min, config.food_max)
        transactions.append({
            'date': date, 'amount': round(-food, 2),
            'type': 'expense', 'category': 'food',
            'description': 'Daily food & household'
        })
        
        # Inventory purchase (vendor) / fuel (gig rider)
        if persona == 'vendor':
            inventory = 0.40 * daily_revenue * np.random.uniform(0.8, 1.2)
            transactions.append({
                'date': date, 'amount': round(-inventory, 2),
                'type': 'expense', 'category': 'inventory',
                'description': 'Daily raw materials'
            })
        elif persona == 'gig_rider':
            fuel = np.random.uniform(4, 8)
            transactions.append({
                'date': date, 'amount': round(-fuel, 2),
                'type': 'expense', 'category': 'fuel',
                'description': 'Daily fuel'
            })
        
        # Monthly expenses (1st of month)
        if date.day == 1:
            rent = config.monthly_rent
            utilities = np.random.uniform(15, 30)
            transactions.append({
                'date': date, 'amount': round(-rent, 2),
                'type': 'expense', 'category': 'rent',
                'description': 'Monthly rent'
            })
            transactions.append({
                'date': date, 'amount': round(-utilities, 2),
                'type': 'expense', 'category': 'utilities',
                'description': 'Monthly utilities'
            })
        
        # Discretionary expenses (random)
        if np.random.random() < 0.15:  # 15% chance per day
            discretionary = np.random.lognormal(2.0, 0.5)
            transactions.append({
                'date': date, 'amount': round(-discretionary, 2),
                'type': 'expense', 'category': 'entertainment',
                'description': 'Discretionary spending'
            })
    
    return pd.DataFrame(transactions)
```

---

## Feature Engineering Pipeline

From raw transactions, we compute **18 features** across 6 categories:

### Category 1: Liquidity & Flow
| # | Feature | Formula |
|:--|:--------|:--------|
| 1 | Average Daily Inflow | $\bar{I} = \frac{1}{T}\sum I_t$ |
| 2 | Average Daily Balance | $ADB = \frac{1}{T}\sum B_t$ |
| 3 | Min Balance / Max Balance Ratio | $\frac{\min(B_t)}{\max(B_t) + \epsilon}$ |

### Category 2: Volatility
| # | Feature | Formula |
|:--|:--------|:--------|
| 4 | Inflow Coefficient of Variation | $CV = \frac{\sigma_I}{\mu_I + \epsilon}$ |
| 5 | Downside Semi-Variance | $SV_{down} = \sqrt{\frac{1}{T}\sum \min(0, I_t - \mu_I)^2}$ |
| 6 | Max Drawdown (Balance) | $\max_t\!\left(\frac{\max_{s \le t} B_s - B_t}{\max_{s \le t} B_s}\right)$ |

### Category 3: Seasonality
| # | Feature | Formula |
|:--|:--------|:--------|
| 7 | Seasonality Ratio | $\frac{\min(\bar{I}_m)}{\max(\bar{I}_m) + \epsilon}$ |
| 8 | Seasonal Amplitude | $\max(\bar{I}_m) - \min(\bar{I}_m)$ |
| 9 | Weekend vs Weekday Ratio | $\frac{\bar{I}_{weekend}}{\bar{I}_{weekday}}$ |

### Category 4: Resilience
| # | Feature | Formula |
|:--|:--------|:--------|
| 10 | Cash Buffer Days | $\frac{ADB}{\text{Avg Daily Burn}}$ |
| 11 | Zero-Income Day Ratio | $\frac{\text{count}(I_t = 0)}{T}$ |
| 12 | Balance Depletion Speed | Days with balance < 15% of max |

### Category 5: Expense Discipline
| # | Feature | Formula |
|:--|:--------|:--------|
| 13 | Essential Expense Ratio | $\frac{E_{ess}}{E_{total}}$ |
| 14 | Discretionary Flexibility | $\phi = \frac{E_{disc}}{E_{total}}$ |
| 15 | Expense-to-Income Ratio | $\frac{E_{total}}{I_{total}}$ |

### Category 6: Behavioral
| # | Feature | Formula |
|:--|:--------|:--------|
| 16 | Income Source Entropy | $-\sum p_i \log_2(p_i)$ |
| 17 | Transaction Frequency | Count of transactions per day |
| 18 | Trend Slope (30d) | Linear regression slope of daily income |

---

## Training Data for Risk Model

To train the LightGBM risk scorer, we generate **200+ synthetic borrowers** with:
- 50 per persona type × 4 risk profiles (low/moderate/high/default)
- 12 months of transaction history each
- Known default labels (generated by simulating whether a fixed EMI would have been missed 3+ times)

> [!TIP]
> The "default" label is generated by running a **counterfactual simulation**: "Would this borrower have defaulted under a traditional fixed EMI?" This creates the ground truth for supervised learning, while also demonstrating exactly why dynamic scheduling prevents those defaults.

### Label Generation Logic
```python
def simulate_fixed_emi_default(transactions_df, loan_principal, annual_rate, tenure_months):
    """Simulate if borrower would default under fixed EMI."""
    emi = calculate_emi(loan_principal, annual_rate, tenure_months)
    missed_payments = 0
    
    for month in range(tenure_months):
        monthly_net = get_monthly_net_cashflow(transactions_df, month)
        if monthly_net < emi:
            missed_payments += 1
    
    return missed_payments >= 3  # Default if 3+ missed payments
```
