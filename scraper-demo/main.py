"""CLI entry point for the scraping framework."""

import argparse
import sys
from pathlib import Path

from exporters import CsvExporter, JsonExporter, SqliteExporter
from scrapers import BooksScraper, QuotesScraper
from utils.logging_config import setup_logging

SCRAPERS = {
    "quotes": QuotesScraper,
    "books": BooksScraper,
}

EXPORTERS = {
    "csv": CsvExporter,
    "json": JsonExporter,
    "sqlite": SqliteExporter,
}

DEFAULT_EXTENSIONS = {
    "csv": ".csv",
    "json": ".json",
    "sqlite": ".db",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Web scraping framework with multiple scrapers and export formats."
    )
    parser.add_argument(
        "--scraper",
        choices=list(SCRAPERS.keys()),
        required=True,
        help="Which scraper to run.",
    )
    parser.add_argument(
        "--format",
        choices=list(EXPORTERS.keys()),
        default="csv",
        help="Output format (default: csv).",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=5,
        help="Maximum number of pages to scrape (default: 5).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (auto-generated if not specified).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0).",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="Book category to scrape (books scraper only).",
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Fetch detail pages for richer data (slower).",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO).",
    )
    return parser.parse_args()


def main() -> None:
    """Run the selected scraper and export results."""
    args = parse_args()
    setup_logging(args.log_level)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    if args.output:
        output_path = args.output
    else:
        ext = DEFAULT_EXTENSIONS[args.format]
        output_path = str(output_dir / f"{args.scraper}{ext}")

    # Build scraper
    if args.scraper == "quotes":
        scraper = QuotesScraper(
            max_pages=args.pages,
            delay=args.delay,
            fetch_authors=args.details,
        )
    elif args.scraper == "books":
        scraper = BooksScraper(
            max_pages=args.pages,
            delay=args.delay,
            category=args.category,
            fetch_details=args.details,
        )
    else:
        print(f"Unknown scraper: {args.scraper}", file=sys.stderr)
        sys.exit(1)

    # Scrape
    with scraper:
        items = scraper.scrape()

    if not items:
        print("No items scraped.")
        sys.exit(0)

    # Export
    exporter_cls = EXPORTERS[args.format]
    if args.format == "sqlite":
        exporter = exporter_cls(output_path, table_name=args.scraper)
    else:
        exporter = exporter_cls(output_path)

    result_path = exporter.export(items)
    print(f"\nDone! {len(items)} items exported to: {result_path}")


if __name__ == "__main__":
    main()
