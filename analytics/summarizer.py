"""
Sales Summarizer — Phase 3 Analytics.

Reads all rows from raw_store_data, aggregates per branch using
Pandas and NumPy, then rewrites the sales_summary table.

Metrics computed per branch:
  - total_sales_amount:       sum of all total_price values
  - number_of_transactions:   count of rows
  - number_of_cashiers:       count of unique cashier names
  - items_sold_count:         sum of all quantity values
  - popular_items:            top 5 items by total quantity (JSON string)
  - rush_hours:               top 5 busiest hours by transaction count (JSON string)
"""

# json: used to serialize popular_items and rush_hours dicts into JSON strings
import json

# datetime: used to timestamp when the summary was generated
from datetime import datetime

# numpy (np): numerical computing — used here for np.round()
import numpy as np

# pandas (pd): data manipulation — used for groupby aggregations
import pandas as pd

# text: SQLAlchemy construct for running raw SQL strings
from sqlalchemy import text

# Import database session factory, engine (for reading tables), and init function
from database.connection import SessionLocal, engine, init_db

# Import the ORM model for the sales_summary table
from models.sales_summary import SalesSummary


class SalesSummarizer:
    """Aggregates raw_store_data into sales_summary, rewriting the table each run."""

    def generate_summary(self):
        """
        Main method: read raw data, compute per-branch summaries,
        and rewrite the sales_summary table with fresh data.
        """
        # Ensure database tables exist
        init_db()

        # Read the entire raw_store_data table into a Pandas DataFrame
        # This uses the SQLAlchemy engine to connect and load the table
        df = pd.read_sql_table("raw_store_data", con=engine)

        # If there's no data in the table, skip the summary
        if df.empty:
            print("  ⚠ No data in raw_store_data — skipping summary.")
            return

        # Compute the aggregated metrics for each branch
        summaries = self._aggregate(df)

        # Write the summaries to the sales_summary table (deletes old data first)
        self._write_summaries(summaries)

    # ── private helpers ──────────────────────────────────────────────

    def _aggregate(self, df: pd.DataFrame) -> list[dict]:
        """
        Compute per-branch summary metrics from the raw data.

        Args:
            df: DataFrame containing all rows from raw_store_data

        Returns:
            List of dicts, each containing one branch's summary metrics.
        """
        results = []

        # Group the data by branch name, then process each branch separately
        for branch, group in df.groupby("branch"):

            # Calculate total revenue: sum of all total_price values, rounded to 2 decimals
            total_sales = float(np.round(group["total_price"].sum(), 2))

            # Count total number of transactions (rows) for this branch
            num_transactions = int(len(group))

            # Count unique cashier names (how many different cashiers worked)
            num_cashiers = int(group["cashier_name"].nunique())

            # Sum up all quantities sold (total number of items sold)
            items_sold = int(group["quantity"].sum())

            # ── Popular Items ──
            # Group by item name, sum quantities, sort descending, take top 5
            popular = (
                group.groupby("item")["quantity"]  # Group by item, look at quantity
                .sum()                              # Sum quantities per item
                .sort_values(ascending=False)       # Sort: highest quantity first
                .head(5)                            # Keep only top 5
            )
            # Convert to a dict: {"Milk": 150, "Bread": 120, ...}
            popular_items = {str(k): int(v) for k, v in popular.items()}

            # ── Rush Hours ──
            # Extract the hour (0-23) from each sold_at timestamp
            group = group.copy()  # Make a copy to avoid SettingWithCopyWarning
            group["hour"] = pd.to_datetime(group["sold_at"]).dt.hour

            # Count transactions per hour, sort descending, take top 5
            hour_counts = (
                group.groupby("hour")          # Group by hour of day
                .size()                         # Count rows per hour
                .sort_values(ascending=False)   # Sort: busiest hours first
                .head(5)                        # Keep only top 5
            )
            # Convert to a dict: {"14": 45, "10": 38, ...}
            rush_hours = {str(k): int(v) for k, v in hour_counts.items()}

            # Build the summary dict for this branch
            results.append(
                {
                    "branch": branch,
                    "total_sales_amount": total_sales,
                    "number_of_transactions": num_transactions,
                    "number_of_cashiers": num_cashiers,
                    "items_sold_count": items_sold,
                    "popular_items": json.dumps(popular_items),   # Serialize dict to JSON string
                    "rush_hours": json.dumps(rush_hours),         # Serialize dict to JSON string
                    "summary_generated_at": datetime.utcnow(),    # Current UTC timestamp
                }
            )

        return results

    def _write_summaries(self, summaries: list[dict]):
        """
        Delete all existing summary rows and insert fresh ones.
        This is a full rewrite (not an update) so the summary always
        reflects the current state of raw_store_data.
        """
        # Create a new database session
        session = SessionLocal()

        try:
            # Delete ALL existing rows from sales_summary table
            # text() wraps raw SQL for execution via SQLAlchemy
            session.execute(text("DELETE FROM sales_summary"))

            # Insert each branch's summary as a new row
            for s in summaries:
                # Unpack the dict as keyword arguments to create a SalesSummary object
                session.add(SalesSummary(**s))

            # Commit the transaction (saves all changes to the database)
            session.commit()
            print(f"  ✔ sales_summary rewritten with {len(summaries)} branch summaries.")

        except Exception as e:
            # If anything fails, rollback all changes
            session.rollback()
            print(f"  ✖ Summary write failed: {e}")
            raise

        finally:
            # Always close the session when done
            session.close()
