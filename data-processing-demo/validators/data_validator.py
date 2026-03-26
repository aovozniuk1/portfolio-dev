"""Data validation step for the ETL pipeline."""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

REQUIRED_COLUMNS = ["date", "product", "quantity", "price", "region", "customer_email"]


@dataclass
class ValidationReport:
    """Summary of validation results."""

    total_rows: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    row_errors: Dict[int, List[str]] = field(default_factory=dict)
    valid_mask: pd.Series = field(default_factory=lambda: pd.Series(dtype=bool))


class DataValidator:
    """Validates incoming sales data against business rules.

    Checks:
        - Required columns are present
        - No null values in required fields
        - Dates are parseable
        - Quantity is a positive integer
        - Price is a positive number
        - Email matches a basic pattern
        - Region is a non-empty string
    """

    def validate(self, df: pd.DataFrame) -> ValidationReport:
        """Run all validation checks on the dataframe.

        Args:
            df: Raw dataframe from the extract stage.

        Returns:
            A ValidationReport with per-row error details.
        """
        report = ValidationReport(total_rows=len(df))
        error_counts: Dict[str, int] = defaultdict(int)
        row_errors: Dict[int, List[str]] = defaultdict(list)

        # Check required columns exist
        missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        for idx, row in df.iterrows():
            errors = self._validate_row(row)
            if errors:
                row_errors[idx] = errors
                for err in errors:
                    error_counts[err] += 1

        valid_mask = pd.Series(True, index=df.index)
        valid_mask[list(row_errors.keys())] = False

        report.valid_mask = valid_mask
        report.valid_count = int(valid_mask.sum())
        report.invalid_count = report.total_rows - report.valid_count
        report.error_counts = dict(error_counts)
        report.row_errors = dict(row_errors)

        return report

    def _validate_row(self, row: pd.Series) -> List[str]:
        """Validate a single row, returning a list of error descriptions."""
        errors = []

        # Null checks
        for col in REQUIRED_COLUMNS:
            if pd.isna(row.get(col)):
                errors.append(f"missing_{col}")

        if errors:
            return errors  # skip further checks if required fields are missing

        # Date
        try:
            pd.to_datetime(row["date"])
        except (ValueError, TypeError):
            errors.append("invalid_date")

        # Quantity
        try:
            qty = int(row["quantity"])
            if qty <= 0:
                errors.append("non_positive_quantity")
        except (ValueError, TypeError):
            errors.append("invalid_quantity")

        # Price
        try:
            price = float(row["price"])
            if price <= 0:
                errors.append("non_positive_price")
        except (ValueError, TypeError):
            errors.append("invalid_price")

        # Email
        email = str(row["customer_email"]).strip()
        if not EMAIL_REGEX.match(email):
            errors.append("invalid_email")

        # Region — quick fix for edge case where pandas reads NaN as string
        region = str(row["region"]).strip()
        if not region or region.lower() == "nan":
            errors.append("empty_region")

        return errors
