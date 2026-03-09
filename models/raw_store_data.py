"""
SQLAlchemy ORM model for the raw_store_data table.

Stores every cleaned sales transaction that has been ingested
from the generated JSON files. This is the main data table
that Phase 2 (ingestion) writes to and Phase 3 (summarizer) reads from.
"""

# datetime: used to set the default value for ingested_at
from datetime import datetime

# SQLAlchemy column types for defining table columns
# Column: defines a column in the table
# DateTime: stores date and time values
# Float: stores decimal numbers (e.g. prices)
# Integer: stores whole numbers
# String: stores text with a max length
from sqlalchemy import Column, DateTime, Float, Integer, String

# Base: the declarative base class all models inherit from
# Importing it registers this model with SQLAlchemy's metadata
from database.connection import Base


class RawStoreData(Base):
    """
    Represents a single sales transaction row in the database.
    Each row corresponds to one item sold at one branch.
    """

    # __tablename__ tells SQLAlchemy what the actual table name is in PostgreSQL
    __tablename__ = "raw_store_data"

    # Primary key column — auto-incrementing integer ID for each record
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Branch name (e.g. "Branch_A") — indexed for fast filtering
    branch = Column(String(50), nullable=False, index=True)

    # Item name (e.g. "Milk", "Bread") — indexed for fast filtering
    item = Column(String(100), nullable=False, index=True)

    # Number of units sold in this transaction
    quantity = Column(Integer, nullable=False)

    # Price per single unit of the item
    unit_price = Column(Float, nullable=False)

    # Total price for this transaction (quantity × unit_price)
    total_price = Column(Float, nullable=False)

    # Timestamp of when the item was sold — indexed for date range queries
    sold_at = Column(DateTime, nullable=False, index=True)

    # Payment method used: "Cash" or "Credit"
    payment_method = Column(String(20), nullable=False)

    # Name of the cashier who processed this sale — indexed for filtering
    cashier_name = Column(String(100), nullable=False, index=True)

    # Timestamp of when this record was inserted into the database
    # Defaults to the current UTC time when the record is created
    ingested_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation for debugging — shows key fields."""
        return (
            f"<RawStoreData(id={self.id}, branch='{self.branch}', "
            f"item='{self.item}', total={self.total_price})>"
        )
