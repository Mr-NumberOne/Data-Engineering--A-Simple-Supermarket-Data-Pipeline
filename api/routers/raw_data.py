"""
Router for raw_store_data endpoints.

Provides full CRUD operations plus filtering by:
  - cashier name
  - branch
  - item
  - date range (start_date / end_date)

Supports pagination via skip & limit query parameters.
"""

# datetime: used for the date range filter parameters
from datetime import datetime

# Optional: allows query parameters to be omitted (None by default)
from typing import Optional

# FastAPI imports:
# APIRouter: groups related endpoints together
# Depends: dependency injection mechanism (used for DB session)
# HTTPException: raises HTTP error responses (e.g. 404 Not Found)
# Query: adds validation and documentation to query parameters
from fastapi import APIRouter, Depends, HTTPException, Query

# Session: SQLAlchemy session type hint for the dependency-injected DB session
from sqlalchemy.orm import Session

# Import our DB session dependency function
from api.dependencies import get_db

# Import Pydantic schemas for request/response validation
from api.schemas.raw_data import RawDataCreate, RawDataResponse, RawDataUpdate

# Import the SQLAlchemy ORM model for the raw_store_data table
from models.raw_store_data import RawStoreData

# Create a router with URL prefix "/raw-data" and Swagger tag "Raw Store Data"
# All endpoints in this router will have URLs starting with /raw-data/
router = APIRouter(prefix="/raw-data", tags=["Raw Store Data"])


# ── LIST (with filters) ─────────────────────────────────────────────

@router.get("/", response_model=list[RawDataResponse])
def list_raw_data(
    # Optional query parameters — each one filters the results if provided
    branch: Optional[str] = Query(None, description="Filter by branch name"),
    cashier: Optional[str] = Query(None, description="Filter by cashier name"),
    item: Optional[str] = Query(None, description="Filter by item name"),
    start_date: Optional[datetime] = Query(None, description="Start of date range (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End of date range (inclusive)"),
    # Pagination parameters
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    # Database session injected by FastAPI via Depends()
    db: Session = Depends(get_db),
):
    """Retrieve raw sales records with optional filters and pagination."""

    # Start building the query — select all columns from raw_store_data
    query = db.query(RawStoreData)

    # Apply filters only if the corresponding parameter was provided
    if branch:
        query = query.filter(RawStoreData.branch == branch)       # Exact match on branch
    if cashier:
        query = query.filter(RawStoreData.cashier_name == cashier) # Exact match on cashier
    if item:
        query = query.filter(RawStoreData.item == item)           # Exact match on item
    if start_date:
        query = query.filter(RawStoreData.sold_at >= start_date)  # sold_at >= start_date
    if end_date:
        query = query.filter(RawStoreData.sold_at <= end_date)    # sold_at <= end_date

    # Order by ID, apply pagination (skip + limit), and execute the query
    records = query.order_by(RawStoreData.id).offset(skip).limit(limit).all()

    # FastAPI automatically converts the ORM objects to RawDataResponse JSON
    return records


# ── GET by ID ────────────────────────────────────────────────────────

@router.get("/{record_id}", response_model=RawDataResponse)
def get_raw_data(record_id: int, db: Session = Depends(get_db)):
    """Retrieve a single raw data record by its ID."""

    # Query for the record with the given ID; .first() returns None if not found
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()

    # If no record was found, return a 404 error
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


# ── CREATE ───────────────────────────────────────────────────────────

@router.post("/", response_model=RawDataResponse, status_code=201)
def create_raw_data(data: RawDataCreate, db: Session = Depends(get_db)):
    """Create a new raw data record from the request body."""

    # Create a new RawStoreData ORM object from the validated Pydantic data
    new_record = RawStoreData(
        branch=data.branch,
        item=data.item,
        quantity=data.quantity,
        unit_price=data.unit_price,
        total_price=data.total_price,
        sold_at=data.sold_at,
        payment_method=data.payment_method,
        cashier_name=data.cashier_name,
    )

    # Add the new record to the session and commit to save it in the database
    db.add(new_record)
    db.commit()

    # Refresh the object to load auto-generated fields (id, ingested_at)
    db.refresh(new_record)

    # Return the newly created record (with id and ingested_at populated)
    return new_record


# ── UPDATE ───────────────────────────────────────────────────────────

@router.put("/{record_id}", response_model=RawDataResponse)
def update_raw_data(record_id: int, data: RawDataUpdate, db: Session = Depends(get_db)):
    """Update an existing raw data record (partial update — only provided fields change)."""

    # Find the existing record by ID
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()

    # Return 404 if the record doesn't exist
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # model_dump(exclude_unset=True) returns only the fields that were
    # explicitly provided in the request (ignores fields left as None)
    update_data = data.model_dump(exclude_unset=True)

    # Update each provided field on the ORM object
    for key, value in update_data.items():
        # setattr(record, "branch", "Branch_B") is equivalent to record.branch = "Branch_B"
        setattr(record, key, value)

    # Save changes to the database
    db.commit()

    # Refresh to get the updated values
    db.refresh(record)

    return record


# ── DELETE ───────────────────────────────────────────────────────────

@router.delete("/{record_id}", status_code=204)
def delete_raw_data(record_id: int, db: Session = Depends(get_db)):
    """Delete a raw data record by ID. Returns HTTP 204 (No Content) on success."""

    # Find the record to delete
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()

    # Return 404 if not found
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Delete the record from the session and commit
    db.delete(record)
    db.commit()
    # No return value needed — HTTP 204 means "success, no content"
