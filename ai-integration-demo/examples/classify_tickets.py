"""Example: Support ticket classification."""

import asyncio
import logging

from services.classifier import ClassifierService

logger = logging.getLogger(__name__)

SAMPLE_TICKETS = [
    "I can't log into my account. I've tried resetting my password three times but I keep getting an error. This is urgent, I need access for a presentation in 2 hours!",
    "Hi, I was charged twice for my subscription this month. Can you please refund the duplicate charge? Order #12345.",
    "It would be great if you could add dark mode to the mobile app. Many of us use the app at night and the bright screen is uncomfortable.",
    "The export to PDF feature crashes every time I try to generate a report with more than 100 rows. I'm on version 3.2.1, Windows 11.",
    "Just wanted to say thanks for the great service! Keep up the good work.",
]


async def run() -> None:
    """Classify a batch of sample support tickets."""
    service = ClassifierService()

    for i, ticket in enumerate(SAMPLE_TICKETS, 1):
        print(f"\n{'='*60}")
        print(f"Ticket #{i}")
        print(f"{'='*60}")
        print(f"  {ticket[:100]}...")

        result = await service.process(ticket)

        print(f"\n  Category:   {result.category.value}")
        print(f"  Priority:   {result.priority.value}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Reasoning:  {result.reasoning}")

    print(f"\n{service.cost_tracker.summary()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
