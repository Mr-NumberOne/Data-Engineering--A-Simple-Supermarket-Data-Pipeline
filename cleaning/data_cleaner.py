"""
Data Cleaner module.

Uses Pandas to clean the raw sales data:
  - Drop rows missing critical fields (item, branch)
  - Fix negative quantities
  - Recalculate total_price from quantity × unit_price
  - Validate payment methods
  - Parse timestamps
  - Remove duplicate rows
"""

# numpy (np): numerical computing library — used here for np.nan (Not-a-Number)
import numpy as np

# pandas (pd): data manipulation library — used to clean data in DataFrames
import pandas as pd

# Import the item catalog (for price lookups) and valid payment methods from settings
from config.settings import ITEM_CATALOG, PAYMENT_METHODS


class DataCleaner:
    """Cleans a list of raw sales-record dicts and returns a clean DataFrame."""

    # List of all column names that must have valid (non-null) values
    # after cleaning. Rows missing any of these will be dropped.
    REQUIRED_COLUMNS = [
        "branch", "item", "quantity", "unit_price",
        "total_price", "sold_at", "payment_method", "cashier_name",
    ]

    def clean(self, records: list[dict]) -> pd.DataFrame:
        """
        Accept raw records (may contain nulls, bad values, duplicates)
        and return a cleaned Pandas DataFrame ready for DB insertion.

        The cleaning pipeline runs 10 steps in order:
        """
        # Convert the list of dictionaries into a Pandas DataFrame
        # Each dict becomes one row; keys become column names
        df = pd.DataFrame(records)

        # If there are no records, return the empty DataFrame immediately
        if df.empty:
            return df

        # Step 1: Drop rows where branch OR item is null (these are required fields)
        df = self._drop_critical_nulls(df)

        # Step 2: Fix quantity — convert to positive integer, default to 1 if null
        df = self._fix_quantity(df)

        # Step 3: Fix unit_price — look up the correct catalog price if the price
        #         is missing or negative; drop rows where price can't be fixed
        df = self._fix_unit_price(df)

        # Step 4: Recalculate total_price from the (now clean) quantity and unit_price
        df = self._recalculate_total(df)

        # Step 5: Validate payment_method — replace invalid values with "Cash" (default)
        df = self._fix_payment_method(df)

        # Step 6: Parse sold_at strings into actual datetime objects;
        #         drop rows with unparseable timestamps
        df = self._parse_timestamps(df)

        # Step 7: Fill any remaining null cashier names with "Unknown"
        df["cashier_name"] = df["cashier_name"].fillna("Unknown")

        # Step 8: Final safety net — drop any rows that still have NaN
        #         in any of the required columns (catches edge cases)
        df = df.dropna(subset=self.REQUIRED_COLUMNS)

        # Step 9: Remove exact duplicate rows (same values in all columns)
        df = df.drop_duplicates()

        # Step 10: Reset the DataFrame index to be consecutive (0, 1, 2, ...)
        #          drop=True means don't keep the old index as a column
        df = df.reset_index(drop=True)

        return df

    # ── private helpers ──────────────────────────────────────────────

    def _drop_critical_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows where branch OR item is null.
        how="any" means drop if ANY of the specified columns is null.
        """
        return df.dropna(subset=["branch", "item"], how="any")

    def _fix_quantity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert quantity to a positive integer.
        - pd.to_numeric with errors="coerce" turns non-numeric values into NaN
        - .abs() makes negative quantities positive
        - .fillna(1) replaces any remaining NaN with 1
        - .astype(int) converts from float to integer
        """
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["quantity"] = df["quantity"].abs().fillna(1).astype(int)
        return df

    def _fix_unit_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace bad or missing unit_prices with the correct price from ITEM_CATALOG.
        If the item isn't in the catalog, set the price to NaN (row will be dropped later).
        """
        # Convert unit_price to numeric, coercing bad values to NaN
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

        # Iterate over each row to check and fix its price
        for idx, row in df.iterrows():
            price = row["unit_price"]

            # If price is missing (NaN) or negative/zero, try to fix it
            if pd.isna(price) or price <= 0:
                # Look up the correct price from the catalog using the item name
                catalog_price = ITEM_CATALOG.get(row.get("item"))

                if catalog_price is not None:
                    # Found the item in catalog — use the correct price
                    df.at[idx, "unit_price"] = catalog_price
                else:
                    # Item not in catalog — mark as NaN for removal
                    df.at[idx, "unit_price"] = np.nan

        # Drop rows where we couldn't determine a valid price
        df = df.dropna(subset=["unit_price"])
        return df

    def _recalculate_total(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recalculate total_price = quantity × unit_price.
        This ensures total_price is always consistent with the cleaned values.
        .round(2) rounds to 2 decimal places for currency precision.
        """
        df["total_price"] = (df["quantity"] * df["unit_price"]).round(2)
        return df

    def _fix_payment_method(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate payment_method values.
        If a value is not in PAYMENT_METHODS ("Cash" or "Credit"),
        replace it with "Cash" as the default.
        The lambda function checks each value individually.
        """
        df["payment_method"] = df["payment_method"].apply(
            lambda v: v if v in PAYMENT_METHODS else "Cash"
        )
        return df

    def _parse_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse sold_at strings (e.g. "2026-03-09 14:30:00") into datetime objects.
        errors="coerce" turns unparseable strings into NaT (Not a Time).
        Then we drop rows where sold_at is NaT (couldn't be parsed).
        """
        df["sold_at"] = pd.to_datetime(df["sold_at"], errors="coerce")
        df = df.dropna(subset=["sold_at"])
        return df
