import os
import pandas as pd
from stock_model.logger import get_logger

logger = get_logger(__name__)


def ensure_dir_exists(path: str):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def save_to_csv(records: list, path: str):
    if not records:
        logger.info("No data to save.")
        return
    ensure_dir_exists(path)
    pd.DataFrame(records).to_csv(path, index=False, encoding="utf-8")
    logger.info(f"Saved data to {path}")


def load_from_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)
