"""Structured entity extraction service."""

import json
import logging

from models.schemas import ExtractedEntities
from services.base import AIServiceBase

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extract named entities from the following text and return them as JSON.

Use this exact structure:
{
  "persons": [{"name": "...", "role": "..."}],
  "organizations": [{"name": "...", "type": "..."}],
  "locations": ["..."],
  "dates": ["..."],
  "monetary_values": ["..."]
}

If a field has no matches, use an empty list. Output ONLY valid JSON, nothing else."""


class EntityExtractorService(AIServiceBase):
    """Extracts structured entities from unstructured text."""

    async def process(self, text: str) -> ExtractedEntities:
        """Extract entities from the given text.

        Args:
            text: Raw text to analyze.

        Returns:
            An ExtractedEntities model with categorized entities.
        """
        messages = [
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": text},
        ]

        result = await self._chat_completion(
            messages=messages,
            temperature=0.0,
            max_tokens=500,
        )

        content = result["content"].strip()

        # Strip markdown code fences if the model wraps them
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        try:
            data = json.loads(content)
            return ExtractedEntities(**data)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed to parse extraction response: %s", exc)
            return ExtractedEntities()
