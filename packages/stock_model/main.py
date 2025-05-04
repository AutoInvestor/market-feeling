import argparse
import sys
from stock_model.logger import get_logger
from stock_model.cli.fetch_companies import main as fetch_companies
from stock_model.cli.fetch_events import main as fetch_events
from stock_model.cli.fetch_news import main as fetch_news
from stock_model.cli.fetch_prices import main as fetch_prices
from stock_model.cli.prepare_dataset import main as prepare_dataset
from stock_model.cli.train_model import main as train_model

logger = get_logger(__name__)
ALL_STEPS = [
    "fetch_companies",
    "fetch_events",
    "fetch_news",
    "fetch_prices",
    "prepare_dataset",
    "train_model",
]


def main():
    parser = argparse.ArgumentParser(description="Market Feeling CLI")
    parser.add_argument(
        "--steps", default=",".join(ALL_STEPS), help="Comma-separated steps to run"
    )
    args = parser.parse_args()
    steps = args.steps.split(",")
    for s in steps:
        if s not in ALL_STEPS:
            logger.error(f"Unknown step: {s}")
            sys.exit(1)
    if "fetch_companies" in steps:
        fetch_companies()
    if "fetch_events" in steps:
        fetch_events()
    if "fetch_news" in steps:
        fetch_news()
    if "fetch_prices" in steps:
        fetch_prices()
    if "prepare_dataset" in steps:
        prepare_dataset()
    if "train_model" in steps:
        train_model()


if __name__ == "__main__":
    main()
