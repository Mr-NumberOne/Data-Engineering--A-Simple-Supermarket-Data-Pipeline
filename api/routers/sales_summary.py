"""
Router for sales_summary endpoints (read-only).

Supports:
  - GET all summaries with optional filters:
      • branch name
      • minimum total sales amount
      • column selection via 'fields' parameter
  - GET summary for a specific branch

Note: This router only supports GET operations.
The sales_summary table is populated by the summarizer (Phase 3), not the API.
"""

# Optional: allows query parameters to be omitted (None by default)
from typing import Optional

# FastAPI imports (same as raw_data router — see that file for details)
from fastapi import APIRouter, Depends, HTTPException, Query

# Session type hint for the database session
from sqlalchemy.orm import Session

# Import our DB session dependency
from api.dependencies import get_db

# Import the Pydantic response schema
from api.schemas.sales_summary import SalesSummaryResponse

# Import the SQLAlchemy ORM model for the sales_summary table
from models.sales_summary import SalesSummary

# Create router with URL prefix "/sales-summary" and Swagger tag
router = APIRouter(prefix="/sales-summary", tags=["Sales Summary"])


# ── LIST ALL (with filters) ─────────────────────────────────────────

@router.get("/", response_model=list[dict])
def list_sales_summaries(
    # Optional filter: only return summaries for this branch
    branch: Optional[str] = Query(None, description="Filter by branch name"),

    # Optional filter: only return branches with sales >= this amount
    min_sales: Optional[float] = Query(None, ge=0, description="Minimum total sales amount"),

    # Optional: comma-separated list of column names to include in the response
    # Example: ?fields=branch,total_sales_amount,popular_items
    fields: Optional[str] = Query(
        None,
        description=(
            "Comma-separated list of columns to include in the response. "
            "Available: branch, total_sales_amount, number_of_transactions, "
            "number_of_cashiers, items_sold_count, popular_items, rush_hours, "
            "summary_generated_at"
        ),
    ),

    # Database session dependency
    db: Session = Depends(get_db),
):
    """
    Retrieve all sales summaries with optional filters.

    Use the 'fields' query parameter to select which columns to return,
    e.g. ?fields=branch,total_sales_amount,popular_items
    """

    # Start building the query
    query = db.query(SalesSummary)

    # Apply branch filter if provided
    if branch:
        query = query.filter(SalesSummary.branch == branch)

    # Apply minimum sales filter if provided
    if min_sales is not None:
        query = query.filter(SalesSummary.total_sales_amount >= min_sales)

    # Execute query, ordered alphabetically by branch name
    summaries = query.order_by(SalesSummary.branch).all()

    # Define all available field names that can be selected
    all_fields = [
        "id", "branch", "total_sales_amount", "number_of_transactions",
        "number_of_cashiers", "items_sold_count", "popular_items",
        "rush_hours", "summary_generated_at",
    ]

    # Determine which fields to include in the response
    if fields:
        # Parse the comma-separated fields string into a list
        requested = [f.strip() for f in fields.split(",")]

        # Always include id and branch for context, plus any valid requested fields
        selected = ["id", "branch"] + [
            f for f in requested
            if f in all_fields and f not in ("id", "branch")  # Avoid duplicates
        ]
    else:
        # If no fields parameter was provided, return all fields
        selected = all_fields

    # Convert ORM objects to dicts with only the selected fields
    result = []
    for s in summaries:
        row = {}
        for f in selected:
            # Get the attribute value from the ORM object
            value = getattr(s, f, None)

            # If the value is a datetime, convert it to ISO format string
            # because datetime objects aren't directly JSON-serializable
            if hasattr(value, "isoformat"):
                value = value.isoformat()

            row[f] = value
        result.append(row)

    return result


# ── GET by branch ────────────────────────────────────────────────────

@router.get("/{branch_name}", response_model=SalesSummaryResponse)
def get_branch_summary(branch_name: str, db: Session = Depends(get_db)):
    """Retrieve the sales summary for a specific branch by name."""

    # Query for the summary matching the given branch name
    summary = (
        db.query(SalesSummary)
        .filter(SalesSummary.branch == branch_name)
        .first()  # Returns None if no match
    )

    # Return 404 if no summary exists for this branch
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"No summary found for branch '{branch_name}'",
        )

    # Return the summary (auto-converted to SalesSummaryResponse by FastAPI)
    return summary
