"""
Pydantic schemas for the raw_store_data endpoints.

Covers Create, Update, and Response models.
These schemas define the structure of request/response JSON bodies
and provide automatic validation via Pydantic.
"""

# datetime: for timestamp fields in the schemas
from datetime import datetime

# Optional: allows fields to be None (used for partial updates)
from typing import Optional

# BaseModel: base class for all Pydantic models — provides validation
# Field: adds extra validation rules and metadata to fields
from pydantic import BaseModel, Field


# ── Create ───────────────────────────────────────────────────────────

class RawDataCreate(BaseModel):
    """
    Schema for creating a new sales record (POST request body).
    All fields are required (no defaults).
    """
    # Field(...) means "required" — the ... is the Pydantic sentinel for required fields
    # example= provides a sample value shown in the Swagger docs

    branch: str = Field(..., example="Branch_A")                    # Which branch made the sale
    item: str = Field(..., example="Milk")                          # What item was sold
    quantity: int = Field(..., ge=1, example=3)                     # How many units (must be >= 1)
    unit_price: float = Field(..., gt=0, example=1.50)              # Price per unit (must be > 0)
    total_price: float = Field(..., gt=0, example=4.50)             # Total = quantity × unit_price
    sold_at: datetime = Field(..., example="2026-03-09T10:30:00")   # When the sale happened
    payment_method: str = Field(..., example="Cash")                # "Cash" or "Credit"
    cashier_name: str = Field(..., example="Nora")                  # Who processed the sale


# ── Update ───────────────────────────────────────────────────────────

class RawDataUpdate(BaseModel):
    """
    Schema for updating an existing sales record (PUT request body).
    All fields are optional — only provided fields will be updated.
    """
    # Optional[str] = None means the field can be omitted from the request
    # If omitted, the existing value in the database won't be changed

    branch: Optional[str] = None
    item: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)      # If provided, must be >= 1
    unit_price: Optional[float] = Field(None, gt=0)  # If provided, must be > 0
    total_price: Optional[float] = Field(None, gt=0)  # If provided, must be > 0
    sold_at: Optional[datetime] = None
    payment_method: Optional[str] = None
    cashier_name: Optional[str] = None


# ── Response ─────────────────────────────────────────────────────────

class RawDataResponse(BaseModel):
    """
    Schema returned when reading a sales record (GET response body).
    Includes all fields plus the auto-generated id and ingested_at.
    """
    id: int                                   # Database primary key
    branch: str                               # Branch name
    item: str                                 # Item name
    quantity: int                             # Quantity sold
    unit_price: float                         # Price per unit
    total_price: float                        # Total price
    sold_at: datetime                         # When the sale happened
    payment_method: str                       # Payment method used
    cashier_name: str                         # Cashier name
    ingested_at: Optional[datetime] = None    # When the record was ingested into DB

    class Config:
        # from_attributes = True tells Pydantic to read data from SQLAlchemy model
        # attributes (obj.branch) instead of dict keys (obj["branch"])
        # This is required for automatic ORM → Pydantic conversion
        from_attributes = True
