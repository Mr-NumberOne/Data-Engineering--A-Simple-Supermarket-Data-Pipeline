"""
Data Generator for Nora's Supermarkets.

Generates realistic (but intentionally dirty) sales transaction data
for multiple branches using Faker and the random module.
Dirty data includes: null values, negative quantities, invalid prices,
and occasional duplicate rows.
"""

import random
from datetime import datetime, timedelta

from faker import Faker

from config.settings import (
    BRANCHES,
    CASHIER_NAMES,
    DIRTY_DATA_PROBABILITY,
    ITEM_CATALOG,
    PAYMENT_METHODS,
)

fake = Faker()


class SalesDataGenerator:
    """Generates batches of sales order records for each supermarket branch."""

    def __init__(self):
        self.items = list(ITEM_CATALOG.keys())
        self.prices = ITEM_CATALOG

    # ── helpers ──────────────────────────────────────────────────────

    def _maybe_null(self, value):
        """Return None with DIRTY_DATA_PROBABILITY chance, else return value."""
        if random.random() < DIRTY_DATA_PROBABILITY:
            return None
        return value

    def _generate_single_record(self, branch: str) -> dict:
        """Create one sales record, with a chance of dirty values."""
        item = random.choice(self.items)
        unit_price = self.prices[item]
        quantity = random.randint(1, 10)

        # ── inject dirty data ──
        # Occasionally make quantity negative
        if random.random() < 0.05:
            quantity = -quantity

        # Occasionally corrupt the unit price
        if random.random() < 0.05:
            unit_price = round(random.uniform(-5.0, 0.0), 2)

        total_price = round(quantity * unit_price, 2)

        # Generate a timestamp within the last 24 hours
        time_offset = random.randint(0, 86400)  # seconds in a day
        sold_at = (datetime.now() - timedelta(seconds=time_offset)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        record = {
            "branch": self._maybe_null(branch),
            "item": self._maybe_null(item),
            "quantity": self._maybe_null(quantity),
            "unit_price": self._maybe_null(unit_price),
            "total_price": self._maybe_null(total_price),
            "sold_at": self._maybe_null(sold_at),
            "payment_method": self._maybe_null(random.choice(PAYMENT_METHODS)),
            "cashier_name": self._maybe_null(random.choice(CASHIER_NAMES)),
        }
        return record

    # ── public API ───────────────────────────────────────────────────

    def generate_batch(self, branch: str, min_rows: int = 15, max_rows: int = 50) -> list[dict]:
        """
        Generate a batch of sales records for a single branch.

        Returns a list of dicts. A small percentage of records will be
        duplicated to simulate real-world dirty data.
        """
        num_records = random.randint(min_rows, max_rows)
        records = [self._generate_single_record(branch) for _ in range(num_records)]

        # Inject duplicates (~5 % of the batch)
        num_duplicates = max(1, int(len(records) * 0.05))
        for _ in range(num_duplicates):
            records.append(random.choice(records).copy())

        random.shuffle(records)
        return records

    def generate_all_branches(self) -> dict[str, list[dict]]:
        """Generate a batch of sales data for every branch.

        Returns:
            dict mapping branch name → list of record dicts
        """
        return {branch: self.generate_batch(branch) for branch in BRANCHES}
