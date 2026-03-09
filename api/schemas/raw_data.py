"""
Pydantic schemas for the raw_store_data endpoints.

Covers Create, Update, Response, and query filter models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Create ───────────────────────────────────────────────────────────
class RawDataCreate(BaseModel):
    """Schema for creating a new sales record."""
    branch: str = Field(..., example="Branch_A")
    item: str = Field(..., example="Milk")
    quantity: int = Field(..., ge=1, example=3)
    unit_price: float = Field(..., gt=0, example=1.50)
    total_price: float = Field(..., gt=0, example=4.50)
    sold_at: datetime = Field(..., example="2026-03-09T10:30:00")
    payment_method: str = Field(..., example="Cash")
    cashier_name: str = Field(..., example="Nora")


# ── Update ───────────────────────────────────────────────────────────
class RawDataUpdate(BaseModel):
    """Schema for updating an existing sales record (all fields optional)."""
    branch: Optional[str] = None
    item: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    unit_price: Optional[float] = Field(None, gt=0)
    total_price: Optional[float] = Field(None, gt=0)
    sold_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    cashier_name: Optional[str] = None


# ── Response ─────────────────────────────────────────────────────────
class RawDataResponse(BaseModel):
    """Schema returned when reading a sales record."""
    id: int
    branch: str
    item: str
    quantity: int
    unit_price: float
    total_price: float
    sold_at: datetime
    payment_method: str
    cashier_name: str
    ingested_at: Optional[datetime] = None

    class Config:
        from_attributes = True
