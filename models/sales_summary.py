"""
SQLAlchemy ORM model for the sales_summary table.

Stores per-branch aggregated analytics that are regenerated
on a schedule (every 4 hours).
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database.connection import Base


class SalesSummary(Base):
    """Aggregated sales summary per branch."""

    __tablename__ = "sales_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch = Column(String(50), nullable=False, unique=True, index=True)
    total_sales_amount = Column(Float, nullable=False, default=0.0)
    number_of_transactions = Column(Integer, nullable=False, default=0)
    number_of_cashiers = Column(Integer, nullable=False, default=0)
    items_sold_count = Column(Integer, nullable=False, default=0)
    popular_items = Column(Text, nullable=True)      # JSON string of top items
    rush_hours = Column(Text, nullable=True)          # JSON string of hour → count
    summary_generated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<SalesSummary(branch='{self.branch}', "
            f"sales={self.total_sales_amount}, txns={self.number_of_transactions})>"
        )
