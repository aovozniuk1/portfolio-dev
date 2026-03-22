"""Base exporter interface."""

from abc import ABC, abstractmethod
from typing import Any, List


class BaseExporter(ABC):
    """Abstract base for all data exporters."""

    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    @abstractmethod
    def export(self, items: List[Any]) -> str:
        """Export items to the configured output.

        Args:
            items: List of dataclass items with a `to_dict()` method.

        Returns:
            Path to the created output file.
        """
