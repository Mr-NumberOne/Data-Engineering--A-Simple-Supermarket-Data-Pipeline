"""
FastAPI Application — Nora's Supermarket Data Pipeline API.

Entry point for Phase 4.  Provides two sets of endpoints:
  1. /raw-data       — full CRUD with filters
  2. /sales-summary  — read-only with filters & column selection

Run with:
    uvicorn api.main:app --reload
"""

# asynccontextmanager: creates an async context manager for the app lifespan
# Used to run code on startup (before serving requests) and shutdown
from contextlib import asynccontextmanager

# FastAPI: the main web framework class — creates the application
from fastapi import FastAPI

# Import our two routers (groups of endpoints)
from api.routers import raw_data, sales_summary

# Import the database initialization function
from database.connection import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager — runs on app startup and shutdown.

    On startup: ensures all database tables exist (creates them if needed).
    On shutdown: nothing needed (connections are handled by the pool).

    The 'yield' separates startup code (before yield) from shutdown code (after yield).
    """
    # ── Startup ──
    init_db()  # Create tables if they don't exist
    yield      # App is now running and serving requests
    # ── Shutdown ──
    # (nothing to clean up)


# Create the FastAPI application instance
app = FastAPI(
    title="Nora's Supermarket Data Pipeline API",    # Shown in Swagger docs header
    description=(                                     # Shown in Swagger docs description
        "REST API for accessing raw sales data and branch-level sales summaries "
        "from Nora's Supermarkets data pipeline."
    ),
    version="1.0.0",          # API version shown in docs
    lifespan=lifespan,         # Attach the lifespan handler for startup/shutdown
)

# ── Include routers ──────────────────────────────────────────────────
# Each router adds its endpoints to the app
# raw_data.router adds: GET/POST/PUT/DELETE /raw-data/...
app.include_router(raw_data.router)

# sales_summary.router adds: GET /sales-summary/...
app.include_router(sales_summary.router)


@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint.
    Returns a simple JSON response to confirm the API is running.
    Useful for monitoring and load balancer health checks.
    """
    return {"status": "ok", "message": "Nora's Supermarket API is running 🏪"}
