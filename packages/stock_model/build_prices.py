import os
import pandas as pd
from stock_model.logger import get_logger
from stock_model.data_manager import load_from_csv, ensure_dir_exists
from stock_model.fetchers import YFinanceFetcher

logger = get_logger(__name__)

def main():
    companies_path = os.path.join(".", "data", "companies.csv")
    df_companies = load_from_csv(companies_path)
    if df_companies.empty:
        logger.info("No companies found. Exiting.")
        return

    tickers = df_companies["ticker"].tolist()
    all_prices = []

    for ticker in tickers:
        logger.info(f"Fetching historical prices for {ticker}...")
        df_prices = YFinanceFetcher.fetch_historical_prices(ticker)
        if df_prices is not None:
            all_prices.append(df_prices)

    if not all_prices:
        logger.info("No price data fetched. Exiting.")
        return

    df_all = pd.concat(all_prices, ignore_index=True)

    output_path = os.path.join(".", "data", "historical_prices.csv")
    ensure_dir_exists(output_path)
    df_all.to_csv(output_path, index=False)
    logger.info(f"Historical prices dataset saved to {output_path}")

if __name__ == "__main__":
    main()
