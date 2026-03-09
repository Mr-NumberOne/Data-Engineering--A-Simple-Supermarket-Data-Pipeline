"""
Data Generator for Nora's Supermarkets.

Generates realistic (but intentionally dirty) sales transaction data
for multiple branches using Faker and the random module.
Dirty data includes: null values, negative quantities, invalid prices,
and occasional duplicate rows.
"""

# random: provides functions for generating random numbers and making random choices
import random

# datetime & timedelta: used to create timestamps within the last 24 hours
from datetime import datetime, timedelta

# Faker: a library that generates realistic fake data (names, dates, etc.)
from faker import Faker

# Import configuration constants from our settings module
from config.settings import (
    BRANCHES,                # List of branch names ["Branch_A", "Branch_B", "Branch_C"]
    CASHIER_NAMES,           # List of cashier names to pick from
    DIRTY_DATA_PROBABILITY,  # Probability (0.15) of making a field null
    ITEM_CATALOG,            # Dict of item names -> unit prices
    PAYMENT_METHODS,         # ["Cash", "Credit"]
)

# Create a Faker instance for generating fake data (we use it for names, etc.)
fake = Faker()


class SalesDataGenerator:
    """Generates batches of sales order records for each supermarket branch."""

    def __init__(self):
        # Extract just the item names (keys) from the catalog into a list
        self.items = list(ITEM_CATALOG.keys())
        # Keep a reference to the full catalog for price lookups
        self.prices = ITEM_CATALOG

    # ── helpers ──────────────────────────────────────────────────────

    def _maybe_null(self, value):
        """
        Randomly decide whether to return the value or None.
        There is a DIRTY_DATA_PROBABILITY (15%) chance of returning None,
        which simulates missing/dirty data in real-world scenarios.
        """
        # random.random() returns a float between 0.0 and 1.0
        if random.random() < DIRTY_DATA_PROBABILITY:
            return None  # Simulate a missing/null value
        return value     # Keep the original value

    def _generate_single_record(self, branch: str) -> dict:
        """
        Create one sales record dictionary, with a chance of dirty values.
        Each field may be randomly set to None by _maybe_null().
        """
        # Pick a random item from the catalog
        item = random.choice(self.items)

        # Look up the correct unit price for the chosen item
        unit_price = self.prices[item]

        # Generate a random quantity between 1 and 10
        quantity = random.randint(1, 10)

        # ── inject dirty data ──

        # 5% chance: make quantity negative (simulates data entry errors)
        if random.random() < 0.05:
            quantity = -quantity

        # 5% chance: replace unit_price with a random negative number (corrupt price)
        if random.random() < 0.05:
            unit_price = round(random.uniform(-5.0, 0.0), 2)

        # Calculate total_price = quantity * unit_price, rounded to 2 decimal places
        total_price = round(quantity * unit_price, 2)

        # Generate a random timestamp within the last 24 hours
        # 86400 = number of seconds in one day (24 * 60 * 60)
        time_offset = random.randint(0, 86400)  # random seconds in a day
        # Subtract the random offset from the current time to get a past timestamp
        sold_at = (datetime.now() - timedelta(seconds=time_offset)).strftime(
            "%Y-%m-%d %H:%M:%S"  # Format: "2026-03-09 14:30:00"
        )

        # Build the record dict; each field is passed through _maybe_null()
        # which has a 15% chance of replacing it with None
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
        # Pick a random number of records to generate (between min_rows and max_rows)
        num_records = random.randint(min_rows, max_rows)

        # Use a list comprehension to generate that many records
        records = [self._generate_single_record(branch) for _ in range(num_records)]

        # Inject duplicate rows (~5% of the batch) to simulate dirty data
        num_duplicates = max(1, int(len(records) * 0.05))  # At least 1 duplicate
        for _ in range(num_duplicates):
            # Pick a random existing record that has already been generated, copy it, and append it
            records.append(random.choice(records).copy())

        # Shuffle the records so duplicates are mixed in randomly
        random.shuffle(records)
        return records

    def generate_all_branches(self) -> dict[str, list[dict]]:
        """
        Generate a batch of sales data for every branch.

        Returns:
            dict mapping branch name → list of record dicts
            Example: {"Branch_A": [{...}, {...}], "Branch_B": [{...}], ...}
        """
        # Use a dict comprehension to generate a batch for each branch
        return {branch: self.generate_batch(branch) for branch in BRANCHES}
