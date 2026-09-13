from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import create_db_and_tables
from app.api import borrowers, cashflow, loans, risk, simulation


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="RaahPay API",
    description="Dynamic Microloan Repayment & Cash-Flow Planning — SDG 8",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(borrowers.router)
app.include_router(cashflow.router)
app.include_router(loans.router)
app.include_router(risk.router)
app.include_router(simulation.router)


@app.get("/")
def root():
    return {
        "app": "RaahPay",
        "version": "1.0.0",
        "docs": "/docs",
        "description": "Dynamic Microloan Repayment & Cash-Flow Planning",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
