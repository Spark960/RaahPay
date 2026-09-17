# RaahPay 🚀

**Dynamic Microloan Repayment & Cash-Flow Planning — SDG 8**

RaahPay is an intelligent platform designed to facilitate dynamic microloan repayments and cash-flow planning. Built to support UN Sustainable Development Goal (SDG) 8 (Decent Work and Economic Growth), RaahPay leverages machine learning to offer adaptive loan management for borrowers with fluctuating incomes, minimizing default risks and improving financial health.

## 🌟 Key Features

- **Dynamic Repayment Models**: Repayment schedules that adapt to the borrower's real-time cash flow and financial situation.
- **Cash-Flow Planning**: Visualizations and forecasting tools to help borrowers manage their finances effectively.
- **Risk Assessment**: Integrated ML models (LightGBM) equipped with SHAP explainability to evaluate risk profiles dynamically.
- **Interactive Dashboards**: Comprehensive frontend built with React, Radix UI, and Recharts to visualize loans, risks, and simulations.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + Vite
- **Styling**: Tailwind CSS, class-variance-authority, clsx
- **Components**: Radix UI (Progress, Slider, Tooltip), Lucide React
- **Data Visualization**: Recharts
- **Routing**: React Router v7

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLModel
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: LightGBM, Scikit-learn, SHAP (Explainability)
- **Other**: Statsmodels, Faker (for mock data generation)

## 📁 Project Structure

```text
m26/
├── backend/          # FastAPI server, ML models, and routing
│   ├── app/          # Core API logic, risk models, cashflow services
│   ├── data/         # Datasets or generated mock data
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/         # React + Vite application
│   ├── src/          # UI Components, pages, assets
│   ├── public/       # Static assets
│   ├── package.json
│   └── tailwind.config.js
├── design-system/    # Shared design assets or guidelines
└── docs/             # Project documentation
```

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+ recommended)
- [Python](https://www.python.org/) (3.9+ recommended)

### 1. Setup the Backend
Navigate to the `backend` directory and set up a virtual environment:
```bash
cd backend
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
# source venv/bin/activate
pip install -r requirements.txt
```

Run the backend server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000` (Swagger docs at `/docs`).

### 2. Setup the Frontend
Open a new terminal, navigate to the `frontend` directory, and install dependencies:
```bash
cd frontend
npm install
```

Start the development server:
```bash
npm run dev
```
The frontend will run on `http://localhost:5173`.

## 🌍 About SDG 8
Goal 8 is about promoting sustained, inclusive and sustainable economic growth, full and productive employment and decent work for all. RaahPay addresses this by offering flexible micro-financing solutions tailored to real-world cash flows, preventing debt traps and encouraging economic participation.
