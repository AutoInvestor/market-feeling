import os
import pandas as pd
from stock_model.fetchers import YFinanceFetcher
from stock_model.data_manager import ensure_dir_exists
from stock_model.logger import get_logger

logger = get_logger(__name__)

NASDAQ100_TICKERS = [
    "AAPL",
    "ABNB",
    "ADBE",
    "ADI",
    "ADP",
    "ADSK",
    "AEP",
    "AMAT",
    "AMD",
    "AMGN",
    "AMZN",
    "ANSS",
    "APP",
    "ARM",
    "ASML",
    "AVGO",
    "AXON",
    "AZN",
    "BIIB",
    "BKNG",
    "BKR",
    "CCEP",
    "CDNS",
    "CDW",
    "CEG",
    "CHTR",
    "CMCSA",
    "COST",
    "CPRT",
    "CRWD",
    "CSCO",
    "CSGP",
    "CSX",
    "CTAS",
    "CTSH",
    "DASH",
    "DDOG",
    "DXCM",
    "EA",
    "EXC",
    "FANG",
    "FAST",
    "FTNT",
    "GEHC",
    "GFS",
    "GILD",
    "GOOG",
    "GOOGL",
    "HON",
    "IDXX",
    "INTC",
    "INTU",
    "ISRG",
    "KDP",
    "KHC",
    "KLAC",
    "LIN",
    "LRCX",
    "LULU",
    "MAR",
    "MCHP",
    "MDB",
    "MDLZ",
    "MELI",
    "META",
    "MNST",
    "MRVL",
    "MSFT",
    "MSTR",
    "MU",
    "NFLX",
    "NVDA",
    "NXPI",
    "ODFL",
    "ON",
    "ORLY",
    "PANW",
    "PAYX",
    "PCAR",
    "PDD",
    "PEP",
    "PLTR",
    "PYPL",
    "QCOM",
    "REGN",
    "ROP",
    "ROST",
    "SBUX",
    "SNPS",
    "TEAM",
    "TMUS",
    "TSLA",
    "TTD",
    "TTWO",
    "TXN",
    "VRSK",
    "VRTX",
    "WBD",
    "WDAY",
    "XEL",
    "ZS",
]


def fetch_nasdaq100_companies() -> list:
    """
    Loops over NASDAQ100_TICKERS, fetching company overview for each ticker.
    Returns a list of dicts, each with ticker, name, sector.
    """
    companies_data = []
    for ticker in NASDAQ100_TICKERS:
        overview = YFinanceFetcher.fetch_company_overview(ticker)
        if overview:
            companies_data.append(overview)
        else:
            logger.warning(f"No overview fetched for {ticker}.")
    return companies_data


def main():
    """
    Main function to build the companies.csv dataset.
    """
    logger.info("Fetching company overviews from yfinance...")
    companies = fetch_nasdaq100_companies()

    if not companies:
        logger.info("No companies fetched.")
        return

    df = pd.DataFrame(companies)
    output_dir = os.path.join(".", "data")
    ensure_dir_exists(output_dir)
    output_path = os.path.join(output_dir, "companies.csv")

    df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Companies dataset saved to {output_path}")


if __name__ == "__main__":
    main()
