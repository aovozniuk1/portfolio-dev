"""Example: Batch processing with concurrency control."""

import asyncio
import logging

from services.batch_processor import BatchProcessor
from services.classifier import ClassifierService

logger = logging.getLogger(__name__)

TICKETS = [
    "My payment was declined but money was taken from my bank account.",
    "How do I change my email address?",
    "App crashes on startup after the latest update.",
    "Can you add integration with Slack?",
    "I need to cancel my subscription immediately, I'm being charged for something I didn't sign up for!",
    "The search function returns no results for any query.",
    "Is there a student discount available?",
    "Getting a 500 error when uploading files larger than 10MB.",
]


async def run() -> None:
    """Process multiple tickets concurrently with bounded parallelism."""
    service = ClassifierService(max_concurrent=3)
    batch = BatchProcessor(max_concurrent=3)

    print(f"Processing {len(TICKETS)} tickets concurrently (max 3 at a time)...\n")

    results = await batch.process(TICKETS, service.process)

    for i, (ticket, result) in enumerate(zip(TICKETS, results), 1):
        if result:
            print(f"  #{i}: [{result.category.value:15s}] [{result.priority.value:6s}] {ticket[:60]}...")
        else:
            print(f"  #{i}: [FAILED] {ticket[:60]}...")

    print(f"\n{service.cost_tracker.summary()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
