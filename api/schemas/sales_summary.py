"""
Pydantic schemas for the sales_summary endpoints.

Read-only — only response models are needed.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SalesSummaryResponse(BaseModel):
    """Schema returned when reading a sales summary record."""
    id: int
    branch: str
    total_sales_amount: float
    number_of_transactions: int
    number_of_cashiers: int
    items_sold_count: int
    popular_items: Optional[str] = None    # JSON string
    rush_hours: Optional[str] = None       # JSON string
    summary_generated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
