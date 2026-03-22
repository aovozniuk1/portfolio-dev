"""SQLite exporter implementation."""

import logging
import sqlite3
from typing import Any, List

from exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class SqliteExporter(BaseExporter):
    """Export scraped items to a SQLite database."""

    def __init__(self, output_path: str, table_name: str = "items") -> None:
        super().__init__(output_path)
        self.table_name = table_name

    def export(self, items: List[Any]) -> str:
        """Write items to a SQLite table.

        Automatically creates the table based on the first item's fields.

        Args:
            items: List of dataclass objects with `to_dict()`.

        Returns:
            Path to the SQLite database file.
        """
        if not items:
            logger.warning("No items to export")
            return self.output_path

        rows = [item.to_dict() for item in items]
        columns = list(rows[0].keys())

        conn = sqlite3.connect(self.output_path)
        try:
            cursor = conn.cursor()

            col_defs = ", ".join(f'"{col}" TEXT' for col in columns)
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
            cursor.execute(f"CREATE TABLE {self.table_name} ({col_defs})")

            placeholders = ", ".join("?" for _ in columns)
            insert_sql = f"INSERT INTO {self.table_name} VALUES ({placeholders})"

            for row in rows:
                values = [
                    str(row[col]) if row[col] is not None else None
                    for col in columns
                ]
                cursor.execute(insert_sql, values)

            conn.commit()
            logger.info(
                "Exported %d items to SQLite table '%s' in %s",
                len(items),
                self.table_name,
                self.output_path,
            )
        finally:
            conn.close()

        return self.output_path
