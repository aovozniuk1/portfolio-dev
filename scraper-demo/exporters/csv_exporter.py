import csv
import logging
from typing import Any, List

from exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class CsvExporter(BaseExporter):
    """Export scraped items to a CSV file."""

    def export(self, items: List[Any]) -> str:
        """Write items to CSV.

        Args:
            items: List of dataclass objects with `to_dict()`.

        Returns:
            Path to the written CSV file.
        """
        if not items:
            logger.warning("No items to export")
            return self.output_path

        rows = [item.to_dict() for item in items]
        fieldnames = list(rows[0].keys())

        with open(self.output_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info("Exported %d items to %s", len(items), self.output_path)
        return self.output_path
