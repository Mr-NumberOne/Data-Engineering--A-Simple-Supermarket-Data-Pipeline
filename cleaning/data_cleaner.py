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

import numpy as np
import pandas as pd

from config.settings import ITEM_CATALOG, PAYMENT_METHODS


class DataCleaner:
    """Cleans a list of raw sales-record dicts and returns a clean DataFrame."""

    REQUIRED_COLUMNS = [
        "branch", "item", "quantity", "unit_price",
        "total_price", "sold_at", "payment_method", "cashier_name",
    ]

    def clean(self, records: list[dict]) -> pd.DataFrame:
        """
        Accept raw records (may contain nulls, bad values, duplicates)
        and return a cleaned Pandas DataFrame ready for DB insertion.
        """
        df = pd.DataFrame(records)

        if df.empty:
            return df

        # 1. Drop rows where critical fields are entirely missing
        df = self._drop_critical_nulls(df)

        # 2. Fix quantity: make absolute, default to 1 if still null
        df = self._fix_quantity(df)

        # 3. Fix unit_price: look up catalog price or drop row
        df = self._fix_unit_price(df)

        # 4. Recalculate total_price
        df = self._recalculate_total(df)

        # 5. Validate & fix payment_method
        df = self._fix_payment_method(df)

        # 6. Parse timestamps
        df = self._parse_timestamps(df)

        # 7. Fill remaining cashier nulls with "Unknown"
        df["cashier_name"] = df["cashier_name"].fillna("Unknown")

        # 8. Final safety: drop rows that still have NaN in any required field
        df = df.dropna(subset=self.REQUIRED_COLUMNS)

        # 9. Remove duplicate rows
        df = df.drop_duplicates()

        # 10. Reset index
        df = df.reset_index(drop=True)

        return df

    # ── private helpers ──────────────────────────────────────────────

    def _drop_critical_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows where branch OR item is null."""
        return df.dropna(subset=["branch", "item"], how="any")

    def _fix_quantity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert quantity to positive int; default to 1 if null."""
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["quantity"] = df["quantity"].abs().fillna(1).astype(int)
        return df

    def _fix_unit_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace bad/missing unit_prices with catalog lookup."""
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

        for idx, row in df.iterrows():
            price = row["unit_price"]
            if pd.isna(price) or price <= 0:
                catalog_price = ITEM_CATALOG.get(row.get("item"))
                if catalog_price is not None:
                    df.at[idx, "unit_price"] = catalog_price
                else:
                    df.at[idx, "unit_price"] = np.nan

        # Drop rows where we couldn't fix the price
        df = df.dropna(subset=["unit_price"])
        return df

    def _recalculate_total(self, df: pd.DataFrame) -> pd.DataFrame:
        """Recalculate total_price = quantity × unit_price."""
        df["total_price"] = (df["quantity"] * df["unit_price"]).round(2)
        return df

    def _fix_payment_method(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace invalid payment methods with 'Cash' (default)."""
        df["payment_method"] = df["payment_method"].apply(
            lambda v: v if v in PAYMENT_METHODS else "Cash"
        )
        return df

    def _parse_timestamps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse sold_at strings to datetime; drop rows that can't be parsed."""
        df["sold_at"] = pd.to_datetime(df["sold_at"], errors="coerce")
        df = df.dropna(subset=["sold_at"])
        return df
