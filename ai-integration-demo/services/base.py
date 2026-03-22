"""Base AI service with retry logic, rate limiting, and error handling."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, APIError, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from utils.config import config
from utils.cost_tracker import CostTracker

logger = logging.getLogger(__name__)


class AIServiceBase(ABC):
    """Abstract base for AI-powered services.

    Provides:
        - AsyncOpenAI client initialization
        - Retry logic with exponential backoff (via tenacity)
        - Rate limiting through asyncio.Semaphore
        - Cost tracking per call
    """

    def __init__(
        self,
        model: Optional[str] = None,
        max_concurrent: Optional[int] = None,
    ) -> None:
        self.model = model or config.openai_model
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.cost_tracker = CostTracker(model=self.model)

        concurrency = max_concurrent or config.max_concurrent_requests
        self._semaphore = asyncio.Semaphore(concurrency)

    @retry(
        retry=retry_if_exception_type((APIError, RateLimitError)),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request with retry and rate limiting.

        Args:
            messages: List of message dicts (role + content).
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            Dict with 'content', 'usage' keys.
        """
        async with self._semaphore:
            logger.debug("Sending request to %s (%d messages)", self.model, len(messages))

            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                kwargs["max_tokens"] = max_tokens

            response = await self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content or ""
            usage = response.usage

            if usage:
                self.cost_tracker.record(
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                )

            return {
                "content": content,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                },
            }

    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Process a single input — implemented by each concrete service."""
