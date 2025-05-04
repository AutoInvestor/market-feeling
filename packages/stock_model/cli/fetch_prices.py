import pandas as pd
from stock_model.fetchers.yfinance_fetcher import YFinanceFetcher
from stock_model.logger import get_logger

logger = get_logger(__name__)


def main(start="2024-01-01", end="2025-05-03"):
    # Load tickers
    df_comp = pd.read_csv("data/companies.csv")
    tickers = df_comp["ticker"].dropna().astype(str).tolist()
    logger.info(f"Fetching prices for {len(tickers)} tickers from {start} to {end}")

    # Fetch and save
    df_all = YFinanceFetcher.fetch_historical_prices(tickers, start, end)
    if df_all.empty:
        logger.warning("No price data fetched for any ticker.")
        return

    df_all.to_csv("data/historical_prices.csv", index=False)
    logger.info("Saved data/historical_prices.csv")
