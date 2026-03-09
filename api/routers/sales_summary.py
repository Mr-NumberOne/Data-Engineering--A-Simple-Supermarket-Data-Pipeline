"""
Router for sales_summary endpoints (read-only).

Supports:
  - GET all summaries with optional filters:
      • branch name
      • minimum total sales amount
      • column selection via 'fields' parameter
  - GET summary for a specific branch
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.sales_summary import SalesSummaryResponse
from models.sales_summary import SalesSummary

router = APIRouter(prefix="/sales-summary", tags=["Sales Summary"])


# ── LIST ALL (with filters) ─────────────────────────────────────────
@router.get("/", response_model=list[dict])
def list_sales_summaries(
    branch: Optional[str] = Query(None, description="Filter by branch name"),
    min_sales: Optional[float] = Query(None, ge=0, description="Minimum total sales amount"),
    fields: Optional[str] = Query(
        None,
        description=(
            "Comma-separated list of columns to include in the response. "
            "Available: branch, total_sales_amount, number_of_transactions, "
            "number_of_cashiers, items_sold_count, popular_items, rush_hours, "
            "summary_generated_at"
        ),
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve all sales summaries with optional filters.

    Use the 'fields' query parameter to select which columns to return,
    e.g. ?fields=branch,total_sales_amount,popular_items
    """
    query = db.query(SalesSummary)

    if branch:
        query = query.filter(SalesSummary.branch == branch)
    if min_sales is not None:
        query = query.filter(SalesSummary.total_sales_amount >= min_sales)

    summaries = query.order_by(SalesSummary.branch).all()

    # Convert to dicts and optionally filter fields
    all_fields = [
        "id", "branch", "total_sales_amount", "number_of_transactions",
        "number_of_cashiers", "items_sold_count", "popular_items",
        "rush_hours", "summary_generated_at",
    ]

    if fields:
        requested = [f.strip() for f in fields.split(",")]
        # Always include id and branch for context
        selected = ["id", "branch"] + [f for f in requested if f in all_fields and f not in ("id", "branch")]
    else:
        selected = all_fields

    result = []
    for s in summaries:
        row = {}
        for f in selected:
            value = getattr(s, f, None)
            # Convert datetime to string for JSON serialization
            if hasattr(value, "isoformat"):
                value = value.isoformat()
            row[f] = value
        result.append(row)

    return result


# ── GET by branch ────────────────────────────────────────────────────
@router.get("/{branch_name}", response_model=SalesSummaryResponse)
def get_branch_summary(branch_name: str, db: Session = Depends(get_db)):
    """Retrieve the sales summary for a specific branch."""
    summary = (
        db.query(SalesSummary)
        .filter(SalesSummary.branch == branch_name)
        .first()
    )
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"No summary found for branch '{branch_name}'",
        )
    return summary
