"""Example: Text summarization with configurable length."""

import asyncio
import logging

from models.schemas import SummaryLength, SummaryRequest
from services.summarizer import SummarizerService

logger = logging.getLogger(__name__)

SAMPLE_TEXT = (
    "Artificial intelligence has transformed the technology landscape in recent years. "
    "Machine learning models are now capable of generating human-quality text, translating "
    "languages in real time, and analyzing complex datasets with remarkable accuracy. "
    "Companies across industries are adopting AI solutions to automate repetitive tasks, "
    "improve customer experiences, and gain competitive advantages. However, the rapid "
    "advancement of AI also raises important questions about ethics, job displacement, "
    "and the need for regulatory frameworks. Researchers and policymakers are working "
    "together to establish guidelines that promote responsible AI development while "
    "fostering innovation. The balance between progress and safety remains one of the "
    "most critical challenges of our time."
)


async def run() -> None:
    """Demonstrate text summarization at different lengths."""
    service = SummarizerService()

    for length in SummaryLength:
        print(f"\n{'='*60}")
        print(f"Summary ({length.value})")
        print("=" * 60)

        request = SummaryRequest(text=SAMPLE_TEXT, length=length)
        response = await service.process(request)

        print(f"\n{response.summary}")
        print(f"\nOriginal: {response.original_length} chars")
        print(f"Summary:  {response.summary_length} chars")
        print(f"Ratio:    {response.compression_ratio:.1%}")

    print(f"\n{service.cost_tracker.summary()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
