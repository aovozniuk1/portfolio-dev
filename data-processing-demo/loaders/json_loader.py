"""JSON loader for the ETL pipeline."""

import json
import logging

logger = logging.getLogger(__name__)


class JsonLoader:
    """Writes a dictionary to a JSON file."""

    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    def load(self, data: dict) -> str:
        """Save the dictionary as formatted JSON.

        Args:
            data: Dictionary to serialize.

        Returns:
            Path to the created file.
        """
        with open(self.output_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, default=str)
        logger.info("Saved summary report to %s", self.output_path)
        return self.output_path
