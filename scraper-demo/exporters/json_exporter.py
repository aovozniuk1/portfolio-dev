"""JSON exporter implementation."""

import json
import logging
from typing import Any, List

from exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class JsonExporter(BaseExporter):
    """Export scraped items to a JSON file."""

    def export(self, items: List[Any]) -> str:
        """Write items to JSON.

        Args:
            items: List of dataclass objects with `to_dict()`.

        Returns:
            Path to the written JSON file.
        """
        data = [item.to_dict() for item in items]

        with open(self.output_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)

        logger.info("Exported %d items to %s", len(items), self.output_path)
        return self.output_path
