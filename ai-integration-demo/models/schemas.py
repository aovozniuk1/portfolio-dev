"""Pydantic models for AI service inputs and outputs."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# --- Summarizer ---

class SummaryLength(str, Enum):
    """Available summary length options."""

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class SummaryRequest(BaseModel):
    """Input for the text summarization use case."""

    text: str = Field(..., min_length=10)
    length: SummaryLength = Field(default=SummaryLength.MEDIUM)
    language: str = Field(default="English")


class SummaryResponse(BaseModel):
    """Output of the text summarization use case."""

    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float


# --- Entity Extractor ---

class PersonEntity(BaseModel):
    """An extracted person entity."""

    name: str
    role: Optional[str] = None


class OrganizationEntity(BaseModel):
    """An extracted organization entity."""

    name: str
    type: Optional[str] = None


class ExtractedEntities(BaseModel):
    """Structured output from entity extraction."""

    persons: List[PersonEntity] = Field(default_factory=list)
    organizations: List[OrganizationEntity] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    monetary_values: List[str] = Field(default_factory=list)


# --- Classifier ---

class TicketCategory(str, Enum):
    """Support ticket categories."""

    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"


class TicketPriority(str, Enum):
    """Inferred ticket priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ClassificationResult(BaseModel):
    """Output of the ticket classification use case."""

    category: TicketCategory
    priority: TicketPriority
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


# --- Cost Tracking ---

class UsageStats(BaseModel):
    """Token and cost tracking for a single API call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
