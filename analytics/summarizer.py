"""
Sales Summarizer — Phase 3 Analytics.

Reads all rows from raw_store_data, aggregates per branch using
Pandas and NumPy, then rewrites the sales_summary table.

Metrics per branch:
  - total_sales_amount
  - number_of_transactions
  - number_of_cashiers (unique)
  - items_sold_count (total quantity)
  - popular_items (top 5 items by quantity)
  - rush_hours (top 5 hours by transaction count)
"""

import json
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import text

from database.connection import SessionLocal, engine, init_db
from models.sales_summary import SalesSummary


class SalesSummarizer:
    """Aggregates raw_store_data into sales_summary, rewriting the table each run."""

    def generate_summary(self):
        """Read raw data, compute summaries, and rewrite the sales_summary table."""
        init_db()

        # Read raw data into a DataFrame
        df = pd.read_sql_table("raw_store_data", con=engine)

        if df.empty:
            print("  ⚠ No data in raw_store_data — skipping summary.")
            return

        summaries = self._aggregate(df)
        self._write_summaries(summaries)

    # ── private helpers ──────────────────────────────────────────────

    def _aggregate(self, df: pd.DataFrame) -> list[dict]:
        """Compute per-branch summary metrics."""
        results = []

        for branch, group in df.groupby("branch"):
            total_sales = float(np.round(group["total_price"].sum(), 2))
            num_transactions = int(len(group))
            num_cashiers = int(group["cashier_name"].nunique())
            items_sold = int(group["quantity"].sum())

            # Top 5 popular items by total quantity sold
            popular = (
                group.groupby("item")["quantity"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )
            popular_items = {str(k): int(v) for k, v in popular.items()}

            # Rush hours: top 5 hours by number of transactions
            group = group.copy()
            group["hour"] = pd.to_datetime(group["sold_at"]).dt.hour
            hour_counts = (
                group.groupby("hour")
                .size()
                .sort_values(ascending=False)
                .head(5)
            )
            rush_hours = {str(k): int(v) for k, v in hour_counts.items()}

            results.append(
                {
                    "branch": branch,
                    "total_sales_amount": total_sales,
                    "number_of_transactions": num_transactions,
                    "number_of_cashiers": num_cashiers,
                    "items_sold_count": items_sold,
                    "popular_items": json.dumps(popular_items),
                    "rush_hours": json.dumps(rush_hours),
                    "summary_generated_at": datetime.utcnow(),
                }
            )

        return results

    def _write_summaries(self, summaries: list[dict]):
        """Truncate sales_summary and insert fresh rows."""
        session = SessionLocal()
        try:
            # Truncate existing summary data (full rewrite)
            session.execute(text("DELETE FROM sales_summary"))

            for s in summaries:
                session.add(SalesSummary(**s))

            session.commit()
            print(f"  ✔ sales_summary rewritten with {len(summaries)} branch summaries.")
        except Exception as e:
            session.rollback()
            print(f"  ✖ Summary write failed: {e}")
            raise
        finally:
            session.close()
