import pandas as pd
import yfinance as yf
from stock_model.logger import get_logger

logger = get_logger(__name__)


class YFinanceFetcher:
    @staticmethod
    def fetch_company_overview(ticker: str) -> dict:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            return {"ticker": ticker.upper(), "name": info.get("shortName", "")}
        except Exception as e:
            logger.warning(f"YFinance overview failed for {ticker}: {e}")
            return {}

    @staticmethod
    def fetch_historical_prices(tickers, start, end):
        """
        Fetches historical prices between start and end dates for one or more tickers,
        returning a long-form DataFrame with columns: date, open, close, ticker.
        """
        # Normalize tickers to list
        symbols = [tickers] if isinstance(tickers, str) else list(tickers)

        # Download data
        df = yf.download(
            symbols, start=start, end=end, progress=False, auto_adjust=False
        )

        if df.empty:
            return pd.DataFrame(columns=["date", "open", "close", "ticker"])

        # Unpivot multi-ticker output
        if isinstance(df.columns, pd.MultiIndex):
            df = (
                df.stack(level=1)
                .reset_index()
                .rename(
                    columns={
                        "Date": "date",
                        "Open": "open",
                        "Close": "close",
                        df.columns.names[1] or "level_1": "ticker",
                    }
                )
            )
        else:
            df = df.reset_index().rename(
                columns={"Date": "date", "Open": "open", "Close": "close"}
            )
            df["ticker"] = symbols[0]

        # Select and order columns, drop any axis names
        df = df[["date", "open", "close", "ticker"]]
        df.index.name = None
        df.columns.name = None

        return df
