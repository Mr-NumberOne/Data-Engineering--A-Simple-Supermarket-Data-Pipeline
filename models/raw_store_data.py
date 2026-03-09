"""
SQLAlchemy ORM model for the raw_store_data table.

Stores every cleaned sales transaction that has been ingested
from the generated JSON files.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from database.connection import Base


class RawStoreData(Base):
    """Represents a single sales transaction row in the database."""

    __tablename__ = "raw_store_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch = Column(String(50), nullable=False, index=True)
    item = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    sold_at = Column(DateTime, nullable=False, index=True)
    payment_method = Column(String(20), nullable=False)
    cashier_name = Column(String(100), nullable=False, index=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<RawStoreData(id={self.id}, branch='{self.branch}', "
            f"item='{self.item}', total={self.total_price})>"
        )
