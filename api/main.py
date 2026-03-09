"""
FastAPI Application — Nora's Supermarket Data Pipeline API.

Entry point for Phase 4.  Provides two sets of endpoints:
  1. /raw-data    — full CRUD with filters
  2. /sales-summary — read-only with filters & column selection

Run with:
    uvicorn api.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers import raw_data, sales_summary
from database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: ensure database tables exist."""
    init_db()
    yield


app = FastAPI(
    title="Nora's Supermarket Data Pipeline API",
    description=(
        "REST API for accessing raw sales data and branch-level sales summaries "
        "from Nora's Supermarkets data pipeline."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── Include routers ──────────────────────────────────────────────────
app.include_router(raw_data.router)
app.include_router(sales_summary.router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Nora's Supermarket API is running 🏪"}
