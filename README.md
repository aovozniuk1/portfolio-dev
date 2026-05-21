# Python Developer Portfolio — Andrii Vozniuk

Working examples demonstrating my Python development skills — bots, APIs, scrapers, data processing, and AI integrations. Each sub-project is self-contained with its own README, requirements, and (where applicable) tests.

## Projects

| Project | Stack | Description |
|---------|-------|-------------|
| [telegram-bot-demo](telegram-bot-demo/) | Python, python-telegram-bot, aiosqlite | Multi-step conversational bot with inline keyboards and form handling |
| [scraper-demo](scraper-demo/) | Python, requests, BeautifulSoup, lxml | Web scraper with pagination, rate limiting, CSV/JSON export |
| [fastapi-demo](fastapi-demo/) | Python, FastAPI, Pydantic, SQLAlchemy | Task Management REST API with CRUD, validation, filtering, JWT auth |
| [data-processing-demo](data-processing-demo/) | Python, Pandas | ETL pipeline — CSV cleaning, transformations, analytics reports |
| [ai-integration-demo](ai-integration-demo/) | Python, OpenAI API | Practical patterns: summarization, extraction, async batch processing |

## Key skills demonstrated

- **Telegram Bots** — ConversationHandler, inline keyboards, multi-step forms, async SQLite
- **Web Scraping** — pagination, exponential backoff, anti-blocking, structured export
- **REST APIs** — FastAPI with async, Pydantic validation, query filtering, JWT auth
- **Data Processing** — Pandas ETL pipelines with CLI interface
- **AI Integration** — OpenAI API patterns, structured output, retry logic, async batch

## How to run

Each sub-project has its own `README.md` with setup and run instructions. Standard pattern:

```bash
cd <sub-project>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                       # where tests are present
```

## License

MIT — use, modify, ship. See [LICENSE](LICENSE).

## About

I'm Andrii Vozniuk, a Senior QA Automation Engineer (currently at N-iX, Kyiv) with 9 years of production experience. This repo holds my Python development work outside the QA-automation lane — APIs, bots, scrapers, AI integrations.

- GitHub: https://github.com/aovozniuk1
- Upwork: [Andrii Vozniuk](https://www.upwork.com/freelancers/~01e825035118b07eda)
- Location: Kyiv, Ukraine
- Other portfolios: [QA frameworks](https://github.com/aovozniuk1/portfolio-qa) · [n8n automation](https://github.com/aovozniuk1/portfolio-n8n) · [LLM evals](https://github.com/aovozniuk1/portfolio-llm-evals)
