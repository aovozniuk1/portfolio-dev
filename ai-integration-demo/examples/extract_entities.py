"""Example: Structured entity extraction from text."""

import asyncio
import logging

from services.entity_extractor import EntityExtractorService

logger = logging.getLogger(__name__)

SAMPLE_TEXT = (
    "On March 15, 2024, Tesla CEO Elon Musk announced a $500 million investment "
    "in a new Gigafactory near Austin, Texas. The facility, developed in partnership "
    "with Samsung Electronics, will focus on next-generation battery technology. "
    "Texas Governor Greg Abbott praised the move, stating it would create over "
    "3,000 jobs in the region. The project is expected to be completed by Q4 2025."
)


async def run() -> None:
    """Demonstrate entity extraction."""
    service = EntityExtractorService()

    print("Input text:")
    print(f"  {SAMPLE_TEXT}\n")

    entities = await service.process(SAMPLE_TEXT)

    print("Extracted entities:")
    print(f"\n  Persons:")
    for p in entities.persons:
        role = f" ({p.role})" if p.role else ""
        print(f"    - {p.name}{role}")

    print(f"\n  Organizations:")
    for o in entities.organizations:
        org_type = f" ({o.type})" if o.type else ""
        print(f"    - {o.name}{org_type}")

    print(f"\n  Locations:")
    for loc in entities.locations:
        print(f"    - {loc}")

    print(f"\n  Dates:")
    for d in entities.dates:
        print(f"    - {d}")

    print(f"\n  Monetary values:")
    for v in entities.monetary_values:
        print(f"    - {v}")

    print(f"\n{service.cost_tracker.summary()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
