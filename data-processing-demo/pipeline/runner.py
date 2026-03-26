"""ETL pipeline orchestrator."""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd

from loaders.csv_loader import CsvLoader
from loaders.json_loader import JsonLoader
from loaders.sqlite_loader import SqliteLoader
from transformers.aggregator import Aggregator
from transformers.cleaner import Cleaner
from validators.data_validator import DataValidator, ValidationReport

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """Collects statistics about a pipeline run."""

    input_rows: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0
    output_rows: int = 0
    elapsed_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)


class Pipeline:
    """Extract -> Validate -> Transform -> Load pipeline.

    Orchestrates the full ETL process: reads raw CSV data, validates it,
    cleans and transforms it, then exports to multiple formats.
    """

    def __init__(self, input_path: str, output_dir: str) -> None:
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.stats = PipelineStats()

    def run(self) -> PipelineStats:
        """Execute all pipeline stages and return run statistics."""
        start = time.time()
        logger.info("Starting pipeline: %s -> %s", self.input_path, self.output_dir)

        # --- Extract ---
        logger.info("Stage 1/4: Extract")
        df = self._extract()
        self.stats.input_rows = len(df)
        logger.info("Loaded %d rows from %s", len(df), self.input_path)

        # --- Validate ---
        logger.info("Stage 2/4: Validate")
        validator = DataValidator()
        report = validator.validate(df)
        self._log_validation_report(report)

        df_valid = df.loc[report.valid_mask].copy()
        self.stats.valid_rows = len(df_valid)
        self.stats.invalid_rows = self.stats.input_rows - self.stats.valid_rows

        if df_valid.empty:
            logger.error("No valid rows after validation — aborting")
            self.stats.errors.append("All rows failed validation")
            return self.stats

        # --- Transform ---
        logger.info("Stage 3/4: Transform")
        cleaner = Cleaner()
        df_clean = cleaner.clean(df_valid)

        aggregator = Aggregator()
        summary = aggregator.aggregate(df_clean)

        # --- Load ---
        logger.info("Stage 4/4: Load")
        self._load(df_clean, summary, report)

        self.stats.output_rows = len(df_clean)
        self.stats.elapsed_seconds = time.time() - start

        logger.info(
            "Pipeline complete: %d/%d rows processed in %.1fs",
            self.stats.output_rows,
            self.stats.input_rows,
            self.stats.elapsed_seconds,
        )
        return self.stats

    def _extract(self) -> pd.DataFrame:
        """Read the input CSV file."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        return pd.read_csv(self.input_path)

    def _log_validation_report(self, report: ValidationReport) -> None:
        """Log validation findings."""
        logger.info(
            "Validation: %d valid, %d invalid out of %d rows",
            report.valid_count,
            report.invalid_count,
            report.total_rows,
        )
        for error_type, count in report.error_counts.items():
            logger.warning("  %s: %d occurrences", error_type, count)

    def _load(
        self,
        df_clean: pd.DataFrame,
        summary: dict,
        report: ValidationReport,
    ) -> None:
        """Export cleaned data and summary to multiple formats."""
        # Cleaned CSV
        csv_path = str(self.output_dir / "cleaned_data.csv")
        CsvLoader(csv_path).load(df_clean)
        # TODO: add parquet support
        logger.info("Exported cleaned CSV: %s", csv_path)

        # Summary JSON report
        summary["validation"] = {
            "total_rows": report.total_rows,
            "valid_rows": report.valid_count,
            "invalid_rows": report.invalid_count,
            "error_counts": report.error_counts,
        }
        json_path = str(self.output_dir / "summary_report.json")
        JsonLoader(json_path).load(summary)
        logger.info("Exported summary JSON: %s", json_path)

        # SQLite database
        db_path = str(self.output_dir / "sales.db")
        SqliteLoader(db_path).load(df_clean)
        logger.info("Exported SQLite database: %s", db_path)
