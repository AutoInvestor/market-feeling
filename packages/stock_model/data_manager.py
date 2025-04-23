import os
import pandas as pd
from stock_model.logger import get_logger

logger = get_logger(__name__)


def ensure_dir_exists(path: str):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def load_from_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)
