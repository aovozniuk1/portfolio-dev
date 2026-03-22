"""Batch processing with async concurrency control."""

import asyncio
import logging
from typing import Any, Callable, Coroutine, List, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class BatchProcessor:
    """Processes a list of items concurrently with a configurable semaphore.

    Useful for sending multiple AI requests while respecting rate limits.
    """

    def __init__(self, max_concurrent: int = 5) -> None:
        self.max_concurrent = max_concurrent

    async def process(
        self,
        items: List[Any],
        processor: Callable[[Any], Coroutine[Any, Any, Any]],
    ) -> List[Any]:
        """Process all items concurrently with bounded parallelism.

        Args:
            items: List of inputs to process.
            processor: Async callable that processes a single item.

        Returns:
            List of results in the same order as inputs.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)
        results: List[Any] = [None] * len(items)

        async def _worker(index: int, item: Any) -> None:
            async with semaphore:
                try:
                    results[index] = await processor(item)
                    logger.debug("Processed item %d/%d", index + 1, len(items))
                except Exception as exc:
                    logger.error("Failed to process item %d: %s", index, exc)
                    results[index] = None

        tasks = [_worker(i, item) for i, item in enumerate(items)]
        await asyncio.gather(*tasks)

        succeeded = sum(1 for r in results if r is not None)
        logger.info("Batch complete: %d/%d succeeded", succeeded, len(items))

        return results
