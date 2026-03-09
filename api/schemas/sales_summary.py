"""
Pydantic schemas for the sales_summary endpoints.

Read-only — only a Response model is needed (no Create/Update).
The sales_summary table is populated by the summarizer, not by the API.
"""

# datetime: for the summary_generated_at field
from datetime import datetime

# Optional: allows fields to be None
from typing import Optional

# BaseModel: base class for Pydantic validation models
from pydantic import BaseModel


class SalesSummaryResponse(BaseModel):
    """
    Schema returned when reading a sales summary record.
    Maps directly to the sales_summary table columns.
    """
    id: int                                             # Database primary key
    branch: str                                         # Branch name (e.g. "Branch_A")
    total_sales_amount: float                           # Total revenue for this branch
    number_of_transactions: int                         # Number of sales transactions
    number_of_cashiers: int                             # Count of unique cashiers
    items_sold_count: int                               # Total items sold (sum of quantities)
    popular_items: Optional[str] = None                 # JSON string: top 5 items by quantity
    rush_hours: Optional[str] = None                    # JSON string: top 5 busiest hours
    summary_generated_at: Optional[datetime] = None     # When this summary was computed

    class Config:
        # from_attributes = True enables automatic conversion from
        # SQLAlchemy ORM objects to this Pydantic model
        from_attributes = True
