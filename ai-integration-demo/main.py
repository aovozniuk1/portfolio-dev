"""CLI entry point for running AI integration examples."""

import argparse
import asyncio
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def main() -> None:
    """Parse arguments and run the selected example."""
    parser = argparse.ArgumentParser(
        description="Run AI integration examples."
    )
    parser.add_argument(
        "example",
        choices=["summarize", "extract", "classify", "batch"],
        help="Which example to run.",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO).",
    )
    args = parser.parse_args()
    setup_logging(args.log_level)

    if args.example == "summarize":
        from examples.summarize import run
    elif args.example == "extract":
        from examples.extract_entities import run
    elif args.example == "classify":
        from examples.classify_tickets import run
    elif args.example == "batch":
        from examples.batch_classify import run
    else:
        print(f"Unknown example: {args.example}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run())


if __name__ == "__main__":
    main()
