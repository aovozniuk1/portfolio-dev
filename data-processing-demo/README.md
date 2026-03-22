# Data Processing Pipeline

An ETL (Extract, Transform, Load) pipeline for processing and analyzing sales data with validation, aggregation, and multi-format output.

## Features

- **Pipeline Pattern** — Clean Extract -> Validate -> Transform -> Load architecture
- **Data Validation** — Type checks, range validation, email format, required fields
- **Cleaning** — Type normalization, string trimming, derived columns (totals, months)
- **Aggregation** — Revenue by region/product, monthly trends, top customers
- **Multiple Outputs** — Cleaned CSV, summary JSON report, SQLite database
- **Statistics** — Row counts, error breakdown, processing time
- **Logging** — Console + file logging with per-stage progress

## Architecture

```
data-processing-demo/
├── main.py                    # CLI entry point
├── generate_sample_data.py    # Sample data generator (550+ rows)
├── sample_data.csv            # Generated test dataset
├── pipeline/
│   └── runner.py              # Pipeline orchestrator
├── validators/
│   └── data_validator.py      # Row-level validation with reports
├── transformers/
│   ├── cleaner.py             # Type casting, normalization, derived cols
│   └── aggregator.py          # Group-by summaries and statistics
├── loaders/
│   ├── csv_loader.py          # CSV output
│   ├── json_loader.py         # JSON report output
│   └── sqlite_loader.py       # SQLite database output
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate sample data
python generate_sample_data.py
```

## Usage

```bash
# Run the pipeline
python main.py --input sample_data.csv --output-dir output

# With custom logging level
python main.py --input sample_data.csv --output-dir output --log-level DEBUG
```

## Output Files

| File                    | Description                                    |
|-------------------------|------------------------------------------------|
| `cleaned_data.csv`     | Validated and cleaned dataset with derived columns |
| `summary_report.json`  | Aggregated statistics and validation report    |
| `sales.db`             | SQLite database with cleaned data              |

## Summary Report Contents

- **Overview** — Total revenue, order count, average order value, date range
- **By Region** — Revenue and orders per geographic region
- **By Product** — Revenue, quantity sold, average price per product
- **Monthly Trends** — Revenue and order count by month
- **Top Customers** — Top 10 customers by total spending
- **Validation** — Row counts and error type breakdown

## Tech Stack

- Python 3.10+
- pandas (data manipulation)
- sqlite3 (database output)
