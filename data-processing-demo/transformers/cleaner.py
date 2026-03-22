"""Data cleaning and enrichment transformations."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class Cleaner:
    """Cleans validated data: type casting, normalization, derived columns."""

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning transformations.

        Args:
            df: Validated dataframe (no invalid rows).

        Returns:
            Cleaned dataframe with additional computed columns.
        """
        df = df.copy()

        # Parse and normalize types
        df["date"] = pd.to_datetime(df["date"])
        df["quantity"] = df["quantity"].astype(int)
        df["price"] = df["price"].astype(float)

        # Normalize strings
        df["product"] = df["product"].str.strip().str.title()
        df["region"] = df["region"].str.strip().str.title()
        df["customer_email"] = df["customer_email"].str.strip().str.lower()

        # Derived columns
        df["total"] = df["quantity"] * df["price"]
        df["month"] = df["date"].dt.to_period("M").astype(str)
        df["day_of_week"] = df["date"].dt.day_name()

        logger.info(
            "Cleaned %d rows: added total, month, day_of_week columns", len(df)
        )
        return df
