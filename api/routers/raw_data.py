"""
Router for raw_store_data endpoints.

Provides full CRUD operations plus filtering by:
  - cashier name
  - branch
  - item
  - date range (start_date / end_date)

Supports pagination via skip & limit query parameters.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas.raw_data import RawDataCreate, RawDataResponse, RawDataUpdate
from models.raw_store_data import RawStoreData

router = APIRouter(prefix="/raw-data", tags=["Raw Store Data"])


# ── LIST (with filters) ─────────────────────────────────────────────
@router.get("/", response_model=list[RawDataResponse])
def list_raw_data(
    branch: Optional[str] = Query(None, description="Filter by branch name"),
    cashier: Optional[str] = Query(None, description="Filter by cashier name"),
    item: Optional[str] = Query(None, description="Filter by item name"),
    start_date: Optional[datetime] = Query(None, description="Start of date range (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="End of date range (inclusive)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """Retrieve raw sales records with optional filters and pagination."""
    query = db.query(RawStoreData)

    if branch:
        query = query.filter(RawStoreData.branch == branch)
    if cashier:
        query = query.filter(RawStoreData.cashier_name == cashier)
    if item:
        query = query.filter(RawStoreData.item == item)
    if start_date:
        query = query.filter(RawStoreData.sold_at >= start_date)
    if end_date:
        query = query.filter(RawStoreData.sold_at <= end_date)

    records = query.order_by(RawStoreData.id).offset(skip).limit(limit).all()
    return records


# ── GET by ID ────────────────────────────────────────────────────────
@router.get("/{record_id}", response_model=RawDataResponse)
def get_raw_data(record_id: int, db: Session = Depends(get_db)):
    """Retrieve a single raw data record by its ID."""
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


# ── CREATE ───────────────────────────────────────────────────────────
@router.post("/", response_model=RawDataResponse, status_code=201)
def create_raw_data(data: RawDataCreate, db: Session = Depends(get_db)):
    """Create a new raw data record."""
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
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


# ── UPDATE ───────────────────────────────────────────────────────────
@router.put("/{record_id}", response_model=RawDataResponse)
def update_raw_data(record_id: int, data: RawDataUpdate, db: Session = Depends(get_db)):
    """Update an existing raw data record (partial update)."""
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


# ── DELETE ───────────────────────────────────────────────────────────
@router.delete("/{record_id}", status_code=204)
def delete_raw_data(record_id: int, db: Session = Depends(get_db)):
    """Delete a raw data record by ID."""
    record = db.query(RawStoreData).filter(RawStoreData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
