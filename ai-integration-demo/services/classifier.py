"""Support ticket classification service."""

import json
import logging

from models.schemas import ClassificationResult, TicketCategory, TicketPriority
from services.base import AIServiceBase

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """You are a support ticket classifier. Analyze the ticket and return JSON with:

{
  "category": "<one of: billing, technical, account, feature_request, bug_report, general>",
  "priority": "<one of: low, medium, high, urgent>",
  "confidence": <float 0.0 to 1.0>,
  "reasoning": "<brief explanation>"
}

Consider urgency indicators, sentiment, and topic to determine priority.
Output ONLY valid JSON, nothing else."""


class ClassifierService(AIServiceBase):
    """Classifies support tickets by category and priority."""

    async def process(self, ticket_text: str) -> ClassificationResult:
        """Classify a support ticket.

        Args:
            ticket_text: The raw ticket content.

        Returns:
            ClassificationResult with category, priority, confidence, and reasoning.
        """
        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": ticket_text},
        ]

        result = await self._chat_completion(
            messages=messages,
            temperature=0.0,
            max_tokens=200,
        )

        content = result["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

        try:
            data = json.loads(content)
            return ClassificationResult(**data)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed to parse classification response: %s", exc)
            return ClassificationResult(
                category=TicketCategory.GENERAL,
                priority=TicketPriority.MEDIUM,
                confidence=0.0,
                reasoning="Failed to parse model response",
            )
