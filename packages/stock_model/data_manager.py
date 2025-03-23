import os
import pandas as pd
from stock_model.logger import get_logger

logger = get_logger(__name__)

def ensure_dir_exists(filepath: str):
    """
    Ensures that the directory for the given filepath exists.
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def save_to_csv(data: list, filepath: str):
    """
    Saves a list of dictionaries to CSV.
    """
    if not data:
        logger.info("No data to save.")
        return
    ensure_dir_exists(filepath)
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Data saved to {filepath}")

def load_from_csv(filepath: str) -> pd.DataFrame:
    """
    Loads data from a CSV file into a pandas DataFrame.
    """
    if not os.path.exists(filepath):
        logger.warning(f"CSV file not found: {filepath}")
        return pd.DataFrame()
    return pd.read_csv(filepath)
