"""Token counting and cost estimation utilities."""

import logging
from typing import Optional

from models.schemas import UsageStats

logger = logging.getLogger(__name__)

# Approximate pricing per 1K tokens (USD) — as of 2025
PRICING = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4": {"input": 0.03, "output": 0.06},
}


class CostTracker:
    """Accumulates token usage and estimates cost across multiple API calls."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.call_count = 0

    def record(self, prompt_tokens: int, completion_tokens: int) -> UsageStats:
        """Record usage from a single API call.

        Args:
            prompt_tokens: Number of tokens in the prompt.
            completion_tokens: Number of tokens in the completion.

        Returns:
            UsageStats for this individual call.
        """
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.call_count += 1

        total = prompt_tokens + completion_tokens
        cost = self._estimate_cost(prompt_tokens, completion_tokens)

        stats = UsageStats(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=round(cost, 6),
        )

        logger.debug(
            "Call #%d: %d tokens ($%.6f)", self.call_count, total, cost
        )
        return stats

    def get_total(self) -> UsageStats:
        """Return cumulative usage statistics."""
        total = self.total_prompt_tokens + self.total_completion_tokens
        cost = self._estimate_cost(
            self.total_prompt_tokens, self.total_completion_tokens
        )
        return UsageStats(
            prompt_tokens=self.total_prompt_tokens,
            completion_tokens=self.total_completion_tokens,
            total_tokens=total,
            estimated_cost_usd=round(cost, 6),
        )

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost in USD."""
        prices = PRICING.get(self.model, PRICING["gpt-4o-mini"])
        input_cost = (prompt_tokens / 1000) * prices["input"]
        output_cost = (completion_tokens / 1000) * prices["output"]
        return input_cost + output_cost

    def summary(self) -> str:
        """Return a human-readable summary string."""
        total = self.get_total()
        return (
            f"API Usage Summary:\n"
            f"  Calls:            {self.call_count}\n"
            f"  Prompt tokens:    {total.prompt_tokens:,}\n"
            f"  Completion tokens:{total.completion_tokens:,}\n"
            f"  Total tokens:     {total.total_tokens:,}\n"
            f"  Estimated cost:   ${total.estimated_cost_usd:.4f}"
        )
