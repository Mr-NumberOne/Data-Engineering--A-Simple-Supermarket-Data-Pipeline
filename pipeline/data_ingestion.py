"""
Data Ingestion Pipeline.

Reads unprocessed JSON files from data/, cleans them via DataCleaner,
inserts the clean rows into the raw_store_data table, and moves the
processed files to data/processed/.
"""

import json
import os
import shutil
from datetime import datetime

from cleaning.data_cleaner import DataCleaner
from config.settings import DATA_DIR, PROCESSED_DIR
from database.connection import SessionLocal, init_db
from models.raw_store_data import RawStoreData


class DataIngestionPipeline:
    """Orchestrates: read files → clean → store in PostgreSQL."""

    def __init__(self):
        self.cleaner = DataCleaner()
        os.makedirs(PROCESSED_DIR, exist_ok=True)

    def run(self):
        """Execute the full ingestion cycle once."""
        # Ensure tables exist
        init_db()

        json_files = self._get_unprocessed_files()
        if not json_files:
            print("  No new files to process.")
            return

        session = SessionLocal()
        total_inserted = 0

        try:
            for filepath in json_files:
                count = self._process_file(filepath, session)
                total_inserted += count

            session.commit()
            print(f"  ✔ Committed {total_inserted} records to raw_store_data.")
        except Exception as e:
            session.rollback()
            print(f"  ✖ Ingestion failed: {e}")
            raise
        finally:
            session.close()

    # ── private helpers ──────────────────────────────────────────────

    def _get_unprocessed_files(self) -> list[str]:
        """Return list of .json file paths in DATA_DIR (excludes processed/)."""
        if not os.path.exists(DATA_DIR):
            return []
        return [
            os.path.join(DATA_DIR, f)
            for f in os.listdir(DATA_DIR)
            if f.endswith(".json") and os.path.isfile(os.path.join(DATA_DIR, f))
        ]

    def _process_file(self, filepath: str, session) -> int:
        """Read, clean, insert, and move a single JSON file. Returns row count."""
        filename = os.path.basename(filepath)
        print(f"  Processing: {filename}")

        with open(filepath, "r", encoding="utf-8") as f:
            records = json.load(f)

        # Clean with Pandas
        df = self.cleaner.clean(records)

        if df.empty:
            print(f"    ⚠ No valid records after cleaning in {filename}")
            self._move_to_processed(filepath)
            return 0

        # Insert into DB
        rows = []
        for _, row in df.iterrows():
            rows.append(
                RawStoreData(
                    branch=row["branch"],
                    item=row["item"],
                    quantity=int(row["quantity"]),
                    unit_price=float(row["unit_price"]),
                    total_price=float(row["total_price"]),
                    sold_at=row["sold_at"],
                    payment_method=row["payment_method"],
                    cashier_name=row["cashier_name"],
                    ingested_at=datetime.utcnow(),
                )
            )
        session.add_all(rows)
        print(f"    ✔ {len(rows)} records staged for insertion")

        # Move file to processed
        self._move_to_processed(filepath)
        return len(rows)

    def _move_to_processed(self, filepath: str):
        """Move a processed file into the processed/ subdirectory."""
        dest = os.path.join(PROCESSED_DIR, os.path.basename(filepath))
        shutil.move(filepath, dest)
