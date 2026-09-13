"""
Synthetic data generator for RaahPay demo.

Three borrower personas:
  A — Street Food Vendor   (high weekend surge, rain shocks)
  B — Seasonal Maize Farmer (harvest peaks Oct-Dec, lean Feb-Apr)
  C — Gig Delivery Rider   (festival spikes, algo variability)

Run:  python data/seed_synthetic.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import math
import random
from datetime import date, timedelta

import numpy as np
from sqlmodel import Session, select

from app.core.database import engine, create_db_and_tables
from app.models import Borrower, Transaction, Loan, Repayment, RiskAssessment

random.seed(42)
np.random.seed(42)

START_DATE = date(2025, 1, 1)
HISTORY_DAYS = 365  # 12 months


# ─────────────────────────────────────────────
# Income generation helpers
# ─────────────────────────────────────────────

def _weekly_factor_vendor(d: date) -> float:
    """Vendors earn more Fri-Sun."""
    factors = [0.70, 0.75, 0.80, 0.85, 1.20, 1.40, 1.30]  # Mon=0 … Sun=6
    return factors[d.weekday()]


def _seasonal_factor_vendor(d: date) -> float:
    """Slight peak during winter festive months (Nov-Jan)."""
    month_factors = {1:1.10, 2:0.90, 3:0.85, 4:0.80, 5:0.90, 6:1.00,
                     7:1.05, 8:1.00, 9:0.95, 10:1.00, 11:1.15, 12:1.25}
    return month_factors[d.month]


def _seasonal_factor_farmer(d: date) -> float:
    """Harvest Oct-Dec, lean Feb-Apr."""
    month_factors = {1:0.70, 2:0.30, 3:0.25, 4:0.40, 5:0.60, 6:0.75,
                     7:0.80, 8:0.85, 9:0.95, 10:1.50, 11:1.80, 12:1.60}
    return month_factors[d.month]


def _gig_event_factor(d: date) -> float:
    """Festival spikes and normal variation."""
    # Diwali (Oct 20-ish), New Year, Eid, etc.
    high_days = {(10, 20), (10, 21), (12, 31), (1, 1), (3, 14), (3, 15)}
    if (d.month, d.day) in high_days:
        return 2.5
    # Weekend boost
    if d.weekday() >= 4:
        return 1.25
    return 1.0


def generate_vendor_income(d: date, base: float) -> float:
    w = _weekly_factor_vendor(d)
    s = _seasonal_factor_vendor(d)
    noise = np.random.lognormal(0, 0.15)
    # Rain shock: ~5% days, income drops 60%
    rain = 0.40 if random.random() < 0.05 else 1.0
    return max(0, base * w * s * noise * rain / 30)


def generate_farmer_income(d: date, base: float) -> float:
    s = _seasonal_factor_farmer(d)
    noise = np.random.lognormal(0, 0.20)
    # Farmers get lumpy income — most days zero, big days on market day
    if random.random() < 0.20:  # 20% chance of income day
        return max(0, base * s * noise * 5)  # compressed 5x because sparse
    return 0.0


def generate_gig_income(d: date, base: float) -> float:
    ef = _gig_event_factor(d)
    noise = np.random.lognormal(0, 0.18)
    # Algorithm penalty: 10% chance gig worker gets throttled
    algo_penalty = 0.30 if random.random() < 0.10 else 1.0
    return max(0, base * ef * noise * algo_penalty / 30)


def generate_expenses(base_income_monthly: float, d: date) -> list[dict]:
    """Generate realistic daily expenses."""
    expenses = []
    # Rent: paid on 1st of month
    if d.day == 1:
        expenses.append({
            "amount": -(base_income_monthly * 0.25),
            "type": "expense", "category": "rent",
            "description": "Monthly rent"
        })
    # Food: daily
    food = base_income_monthly * 0.08 / 30
    expenses.append({
        "amount": -abs(np.random.normal(food, food * 0.2)),
        "type": "expense", "category": "food",
        "description": "Daily food"
    })
    # Inventory/supplies: random days
    if random.random() < 0.15:
        inv = base_income_monthly * 0.10 / 30 * 5
        expenses.append({
            "amount": -abs(np.random.normal(inv, inv * 0.3)),
            "type": "expense", "category": "inventory",
            "description": "Business supplies"
        })
    # Utilities: on 5th of month
    if d.day == 5:
        expenses.append({
            "amount": -(base_income_monthly * 0.05),
            "type": "expense", "category": "utilities",
            "description": "Utilities"
        })
    return expenses


# ─────────────────────────────────────────────
# Loan helpers
# ─────────────────────────────────────────────

def compute_emi(principal: float, annual_rate: float, months: int) -> float:
    r = annual_rate / 12
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def build_fixed_schedule(loan_id: int, principal: float, annual_rate: float,
                         months: int, start: date) -> list[dict]:
    emi = compute_emi(principal, annual_rate, months)
    r = annual_rate / 12
    balance = principal
    rows = []
    for i in range(1, months + 1):
        interest = balance * r
        principal_comp = emi - interest
        balance -= principal_comp
        rows.append(dict(
            loan_id=loan_id, period_number=i,
            due_date=start + timedelta(days=30 * i),
            scheduled_amount=round(emi, 2),
            principal_component=round(principal_comp, 2),
            interest_component=round(interest, 2),
            remaining_balance=round(max(0, balance), 2),
            status="pending", adjustment_reason="standard"
        ))
    return rows


# ─────────────────────────────────────────────
# Persona definitions
# ─────────────────────────────────────────────

PERSONAS = [
    {
        "name": "Raju Kumar",
        "persona_type": "vendor",
        "base_monthly_income": 1200.0,
        "location": "Crawford Market, Mumbai",
        "loan_principal": 5000.0,
        "income_fn": generate_vendor_income,
    },
    {
        "name": "Meena Devi",
        "persona_type": "farmer",
        "base_monthly_income": 800.0,
        "location": "Nashik District, Maharashtra",
        "loan_principal": 3000.0,
        "income_fn": generate_farmer_income,
    },
    {
        "name": "Arjun Patil",
        "persona_type": "gig_worker",
        "base_monthly_income": 1500.0,
        "location": "Bengaluru, Karnataka",
        "loan_principal": 7000.0,
        "income_fn": generate_gig_income,
    },
]


# ─────────────────────────────────────────────
# Main seeder
# ─────────────────────────────────────────────

def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # Clear existing data
        for model in [RiskAssessment, Repayment, Loan, Transaction, Borrower]:
            rows = session.exec(select(model)).all()
            for r in rows:
                session.delete(r)
        session.commit()

        for persona in PERSONAS:
            # 1. Create borrower
            borrower = Borrower(
                name=persona["name"],
                persona_type=persona["persona_type"],
                base_monthly_income=persona["base_monthly_income"],
                location=persona["location"],
                registered_at=START_DATE,
                status="active",
            )
            session.add(borrower)
            session.commit()
            session.refresh(borrower)

            # 2. Generate 12 months of transactions
            income_fn = persona["income_fn"]
            base = persona["base_monthly_income"]

            for day_offset in range(HISTORY_DAYS):
                d = START_DATE + timedelta(days=day_offset)

                # Income
                income = income_fn(d, base)
                if income > 0.01:
                    cat = {"vendor": "sales", "farmer": "sales", "gig_worker": "wages"}[persona["persona_type"]]
                    session.add(Transaction(
                        borrower_id=borrower.id,
                        transaction_date=d,
                        amount=round(income, 2),
                        type="income",
                        category=cat,
                        description=f"{persona['persona_type'].replace('_',' ').title()} daily income",
                    ))

                # Expenses
                for exp in generate_expenses(base, d):
                    session.add(Transaction(
                        borrower_id=borrower.id,
                        transaction_date=d,
                        amount=round(exp["amount"], 2),
                        type=exp["type"],
                        category=exp["category"],
                        description=exp["description"],
                    ))

            session.commit()

            # 3. Create loan (disbursed 6 months into history — so we have pre-loan data)
            disburse_date = START_DATE + timedelta(days=180)
            principal = persona["loan_principal"]
            rate = 0.18
            tenure = 12
            emi = compute_emi(principal, rate, tenure)

            loan = Loan(
                borrower_id=borrower.id,
                principal=principal,
                annual_interest_rate=rate,
                original_tenure_months=tenure,
                adjusted_tenure_months=tenure,
                base_emi=round(emi, 2),
                disbursement_date=disburse_date,
                status="active",
                schedule_type="dynamic",
            )
            session.add(loan)
            session.commit()
            session.refresh(loan)

            # 4. Build repayment schedule (6 periods completed, 6 pending)
            r_monthly = rate / 12
            balance = principal
            for i in range(1, tenure + 1):
                interest_comp = balance * r_monthly
                principal_comp = emi - interest_comp
                balance -= principal_comp
                due = disburse_date + timedelta(days=30 * i)

                if i <= 6:
                    # Historical payments — simulate dynamic adjustment
                    month_date = disburse_date + timedelta(days=30 * (i - 1))
                    season_factor = _seasonal_factor_vendor(month_date) if persona["persona_type"] == "vendor" \
                        else _seasonal_factor_farmer(month_date) if persona["persona_type"] == "farmer" \
                        else _gig_event_factor(month_date)
                    adj_factor = 0.80 + (season_factor - 1.0) * 0.4
                    adj_factor = max(0.5, min(1.5, adj_factor))
                    actual = round(emi * adj_factor, 2)
                    status = "paid"
                    reason = "surplus_available" if adj_factor > 1 else ("seasonal_low" if adj_factor < 0.9 else "standard")
                else:
                    actual = 0.0
                    status = "pending"
                    reason = "standard"

                session.add(Repayment(
                    loan_id=loan.id,
                    period_number=i,
                    due_date=due,
                    scheduled_amount=round(emi, 2),
                    actual_amount=actual,
                    principal_component=round(principal_comp, 2),
                    interest_component=round(interest_comp, 2),
                    remaining_balance=round(max(0, balance), 2),
                    status=status,
                    adjustment_reason=reason,
                ))

            session.commit()
            print(f"[OK] Seeded: {borrower.name} ({persona['persona_type']}) -- loan ${principal}, EMI ${emi:.2f}")

    print("\n[DONE] Database seeded successfully! demo.db is ready.")


if __name__ == "__main__":
    seed()
