import pandas as pd
from stock_model.data_manager import load_from_csv, save_to_csv
from stock_model.logger import get_logger

logger = get_logger(__name__)

def create_training_dataset(news_path: str, prices_path: str, output_path: str):
    """
    Loads historical news and stock prices, merges them on ticker/date, and calculates a 1-day return.
    The result is saved as a new CSV for further processing.
    """

    # 1) Load CSVs using our unified data_manager
    news_df = load_from_csv(news_path)
    prices_df = load_from_csv(prices_path)

    # 2) Rename the 'Date' column in prices to match 'date' in the news dataset
    if 'Date' in prices_df.columns:
        prices_df.rename(columns={'Date': 'date'}, inplace=True)

    # 3) Ensure both 'date' columns are proper date types (drop timezones if any)
    news_df['date'] = pd.to_datetime(news_df['date'], utc=True).dt.date
    prices_df['date'] = pd.to_datetime(prices_df['date'], utc=True).dt.date

    # 4) Sort by ticker and date to safely shift
    prices_df.sort_values(by=['ticker', 'date'], inplace=True)

    # 5) Calculate the 1-day forward return
    #    (Close of next day - Close of current day) / Close of current day
    #    We group by ticker so that each ticker’s shift is isolated from the others.
    prices_df['return_1d'] = (
        prices_df.groupby('ticker')['Close'].shift(-1) - prices_df['Close']
    ) / prices_df['Close']

    # 6) Merge news and price data on ticker & date
    merged_df = pd.merge(
        news_df,
        prices_df[['ticker', 'date', 'return_1d']],
        on=['ticker', 'date'],
        how='inner'
    )

    columns_to_drop = ['name', 'title', 'url', 'summary']
    merged_df.drop(columns_to_drop, axis=1, inplace=True)

    save_to_csv(merged_df.to_dict('records'), output_path)
    logger.info(f"Training dataset saved to {output_path}")


def main():
    news_path = './data/historical_news.csv'
    prices_path = './data/historical_prices.csv'
    output_path = './data/news_stock_dataset.csv'

    create_training_dataset(news_path, prices_path, output_path)

if __name__ == "__main__":
    main()
