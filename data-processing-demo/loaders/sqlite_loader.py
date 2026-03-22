"""SQLite loader for the ETL pipeline."""

import logging
import sqlite3

import pandas as pd

logger = logging.getLogger(__name__)


class SqliteLoader:
    """Writes a dataframe to a SQLite database table."""

    def __init__(self, db_path: str, table_name: str = "sales") -> None:
        self.db_path = db_path
        self.table_name = table_name

    def load(self, df: pd.DataFrame) -> str:
        """Save the dataframe to a SQLite table (replaces existing).

        Args:
            df: Dataframe to persist.

        Returns:
            Path to the database file.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            df.to_sql(self.table_name, conn, if_exists="replace", index=False)
            logger.info(
                "Saved %d rows to table '%s' in %s",
                len(df),
                self.table_name,
                self.db_path,
            )
        finally:
            conn.close()
        return self.db_path
