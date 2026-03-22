"""Text summarization service."""

import logging

from models.schemas import SummaryLength, SummaryRequest, SummaryResponse
from services.base import AIServiceBase

logger = logging.getLogger(__name__)

LENGTH_INSTRUCTIONS = {
    SummaryLength.SHORT: "Summarize in 1-2 sentences.",
    SummaryLength.MEDIUM: "Summarize in a short paragraph (3-5 sentences).",
    SummaryLength.LONG: "Provide a detailed summary covering all key points (6-10 sentences).",
}

MAX_TOKENS_MAP = {
    SummaryLength.SHORT: 100,
    SummaryLength.MEDIUM: 300,
    SummaryLength.LONG: 600,
}


class SummarizerService(AIServiceBase):
    """Summarizes text with configurable output length."""

    async def process(self, request: SummaryRequest) -> SummaryResponse:
        """Summarize the given text.

        Args:
            request: A SummaryRequest with text, desired length, and language.

        Returns:
            SummaryResponse with the summary and compression stats.
        """
        instruction = LENGTH_INSTRUCTIONS[request.length]
        system_prompt = (
            f"You are a professional text summarizer. {instruction} "
            f"Respond in {request.language}. Output only the summary, no preamble."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text},
        ]

        result = await self._chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=MAX_TOKENS_MAP[request.length],
        )

        summary_text = result["content"].strip()
        original_len = len(request.text)
        summary_len = len(summary_text)

        return SummaryResponse(
            summary=summary_text,
            original_length=original_len,
            summary_length=summary_len,
            compression_ratio=round(summary_len / original_len, 3) if original_len else 0,
        )
