"""
SQLAlchemy ORM model for the sales_summary table.

Stores per-branch aggregated analytics that are regenerated
on a schedule (every 4 hours). Each row contains a full
summary of one branch's sales performance.
"""

# datetime: used to set default value for summary_generated_at
from datetime import datetime

# SQLAlchemy column types
# Text: stores long strings (used for JSON data that may be large)
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

# Base: the declarative base that registers this model with SQLAlchemy
from database.connection import Base


class SalesSummary(Base):
    """
    Aggregated sales summary per branch.
    Rewritten entirely every 4 hours by the summarizer.
    """

    # The actual table name in PostgreSQL
    __tablename__ = "sales_summary"

    # Primary key — auto-incrementing ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Branch name — unique constraint ensures one summary row per branch
    # indexed for fast lookups
    branch = Column(String(50), nullable=False, unique=True, index=True)

    # Total revenue from all sales at this branch (sum of all total_price values)
    total_sales_amount = Column(Float, nullable=False, default=0.0)

    # Total number of individual transactions (rows in raw_store_data)
    number_of_transactions = Column(Integer, nullable=False, default=0)

    # Count of unique cashier names who processed sales at this branch
    number_of_cashiers = Column(Integer, nullable=False, default=0)

    # Total quantity of all items sold (sum of all quantity values)
    items_sold_count = Column(Integer, nullable=False, default=0)

    # JSON string of the top 5 most popular items by quantity
    # Example: '{"Milk": 150, "Bread": 120, "Eggs (12)": 95, ...}'
    popular_items = Column(Text, nullable=True)

    # JSON string of the top 5 busiest hours by transaction count
    # Example: '{"14": 45, "10": 38, "16": 35, ...}' (keys are hours 0-23)
    rush_hours = Column(Text, nullable=True)

    # Timestamp of when this summary was generated
    # Defaults to the current UTC time
    summary_generated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation for debugging — shows branch, sales, and transaction count."""
        return (
            f"<SalesSummary(branch='{self.branch}', "
            f"sales={self.total_sales_amount}, txns={self.number_of_transactions})>"
        )
