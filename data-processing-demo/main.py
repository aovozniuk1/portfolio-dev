"""CLI entry point for the data processing pipeline."""

import argparse
import logging
import sys

from pipeline.runner import Pipeline


def setup_logging(level: str = "INFO") -> None:
    """Configure console and file logging."""
    log_format = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pipeline.log", encoding="utf-8"),
    ]
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=handlers,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ETL pipeline for processing sales data."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for output files (default: output).",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity (default: INFO).",
    )
    return parser.parse_args()


def main() -> None:
    """Run the ETL pipeline from command-line arguments."""
    args = parse_args()
    setup_logging(args.log_level)

    pipeline = Pipeline(input_path=args.input, output_dir=args.output_dir)

    try:
        stats = pipeline.run()
    except FileNotFoundError as exc:
        logging.error(str(exc))
        sys.exit(1)
    except ValueError as exc:
        logging.error("Data error: %s", exc)
        sys.exit(1)

    # Print summary
    print("\n" + "=" * 50)
    print("Pipeline Summary")
    print("=" * 50)
    print(f"  Input rows:     {stats.input_rows}")
    print(f"  Valid rows:     {stats.valid_rows}")
    print(f"  Invalid rows:   {stats.invalid_rows}")
    print(f"  Output rows:    {stats.output_rows}")
    print(f"  Time elapsed:   {stats.elapsed_seconds:.2f}s")

    if stats.errors:
        print(f"  Errors:         {', '.join(stats.errors)}")

    print(f"\nOutput files in: {args.output_dir}/")


if __name__ == "__main__":
    main()
