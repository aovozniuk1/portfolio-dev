# Web Scraping Framework

A modular scraping framework with pluggable scrapers, multiple export formats, and built-in anti-blocking measures.

## Features

- **Pluggable Scrapers** — Base class with retry logic, rate limiting, and session management
- **Quotes Scraper** — Scrapes quotes.toscrape.com with pagination and optional author details
- **Books Scraper** — Scrapes books.toscrape.com with categories, prices, ratings, and stock info
- **Multiple Export Formats** — CSV, JSON, and SQLite via a common exporter interface
- **Anti-Blocking** — User-Agent rotation, configurable delays, exponential backoff on retries
- **Rotating Logs** — File-based logging with automatic rotation at 5 MB

## Architecture

```
scraper-demo/
├── main.py              # CLI entry point (argparse)
├── scrapers/
│   ├── base.py          # BaseScraper ABC with retry/rate-limit
│   ├── quotes.py        # QuotesScraper implementation
│   └── books.py         # BooksScraper implementation
├── models/
│   └── items.py         # Dataclass models (Quote, Author, Book)
├── exporters/
│   ├── base.py          # BaseExporter ABC
│   ├── csv_exporter.py  # CSV output
│   ├── json_exporter.py # JSON output
│   └── sqlite_exporter.py # SQLite output
├── utils/
│   ├── helpers.py       # User-Agent rotation
│   └── logging_config.py # Rotating file handler setup
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Scrape quotes to CSV (2 pages)
python main.py --scraper quotes --format csv --pages 2

# Scrape books to JSON with category filter
python main.py --scraper books --format json --pages 3 --category travel

# Scrape books to SQLite with detail pages
python main.py --scraper books --format sqlite --pages 5 --details

# Full options
python main.py --scraper quotes --format json --pages 10 --delay 2.0 --details --log-level DEBUG
```

## CLI Options

| Flag          | Description                              | Default |
|---------------|------------------------------------------|---------|
| `--scraper`   | Scraper to run (`quotes` / `books`)      | —       |
| `--format`    | Export format (`csv` / `json` / `sqlite`)| `csv`   |
| `--pages`     | Max pages to scrape                      | `5`     |
| `--output`    | Custom output file path                  | auto    |
| `--delay`     | Seconds between requests                 | `1.0`   |
| `--category`  | Book category (books only)               | all     |
| `--details`   | Fetch detail pages for richer data       | off     |
| `--log-level` | DEBUG / INFO / WARNING / ERROR           | `INFO`  |

## Tech Stack

- Python 3.10+
- requests + urllib3 (HTTP with retry)
- BeautifulSoup4 + lxml (HTML parsing)
