import logging

import pandas as pd

logger = logging.getLogger(__name__)


class CsvLoader:
    """Writes a dataframe to a CSV file."""

    def __init__(self, output_path: str) -> None:
        self.output_path = output_path

    def load(self, df: pd.DataFrame) -> str:
        """Save the dataframe as CSV.

        Args:
            df: Dataframe to save.

        Returns:
            Path to the created file.
        """
        df.to_csv(self.output_path, index=False)
        logger.info("Saved %d rows to %s", len(df), self.output_path)
        return self.output_path
