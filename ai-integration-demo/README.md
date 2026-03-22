# AI Integration Patterns

Professional patterns for integrating OpenAI's API into Python applications, featuring retry logic, rate limiting, cost tracking, and structured outputs.

## Features

- **Base Service Class** — Retry with exponential backoff (tenacity), rate limiting (semaphore), error handling
- **Text Summarizer** — Configurable output length (short/medium/long), multi-language support
- **Entity Extractor** — Extracts persons, organizations, locations, dates, and monetary values into Pydantic models
- **Ticket Classifier** — Categorizes support tickets by type and priority with confidence scores
- **Batch Processor** — Concurrent processing with bounded parallelism via asyncio.Semaphore
- **Cost Tracking** — Token counting and USD cost estimation per call and cumulative
- **Pydantic Models** — Typed inputs and outputs for every use case

## Architecture

```
ai-integration-demo/
├── main.py                  # CLI to run examples
├── services/
│   ├── base.py              # AIServiceBase (retry, rate limit, cost tracking)
│   ├── summarizer.py        # Text summarization service
│   ├── entity_extractor.py  # Structured entity extraction
│   ├── classifier.py        # Support ticket classification
│   └── batch_processor.py   # Concurrent batch processing
├── models/
│   └── schemas.py           # Pydantic models for all inputs/outputs
├── utils/
│   ├── config.py            # Environment-based configuration
│   └── cost_tracker.py      # Token + cost estimation
├── examples/
│   ├── summarize.py         # Summarization demo
│   ├── extract_entities.py  # Entity extraction demo
│   ├── classify_tickets.py  # Classification demo
│   └── batch_classify.py    # Batch processing demo
├── requirements.txt
└── .env.example
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Usage

```bash
# Run individual examples
python main.py summarize
python main.py extract
python main.py classify
python main.py batch

# With debug logging
python main.py classify --log-level DEBUG
```

## Examples

### Text Summarization
Summarizes input text at three configurable lengths with compression ratio reporting.

### Entity Extraction
Extracts structured data from unstructured text and returns it as a validated Pydantic model.

### Ticket Classification
Classifies support tickets into categories (billing, technical, bug report, etc.) with priority levels and confidence scores.

### Batch Processing
Processes multiple items concurrently with a configurable parallelism limit, demonstrating production-ready async patterns.

## Key Patterns

- **Retry with Backoff** — Automatic retry on API errors and rate limits using tenacity
- **Rate Limiting** — asyncio.Semaphore prevents exceeding concurrent request limits
- **Structured Outputs** — JSON parsing with Pydantic validation for type safety
- **Cost Estimation** — Per-call and cumulative token/cost tracking
- **Error Isolation** — Failed items in batch processing don't block other items

## Tech Stack

- Python 3.10+
- openai (async client)
- tenacity (retry logic)
- pydantic v2 (schemas and validation)
- tiktoken (token counting)
- python-dotenv (configuration)
