import os
import pandas as pd
import requests
import glob
from datetime import datetime, timedelta

from stock_model.logger import get_logger
from stock_model.data_manager import ensure_dir_exists
from stock_model.fetchers.yfinance_fetcher import YFinanceFetcher
from stock_model.fetchers.gdelt_fetcher import GdeltFetcher
from stock_model.analyzers.textblob_analyzer import TextBlobAnalyzer
from stock_model.analyzers.finbert_analyzer import FinBertAnalyzer
from stock_model.analyzers.spacy_analyzer import SpacySimilarityAnalyzer
from stock_model.scrapers.NewspaperScraper import NewspaperScraper

logger = get_logger(__name__)
NASDAQ100 = ["AAPL", "MDB", "GOOGL"]


def fetch_companies_csv(path: str):
    companies = []
    for t in NASDAQ100:
        ov = YFinanceFetcher.fetch_company_overview(t)
        if ov:
            companies.append(ov)
    pd.DataFrame(companies).to_csv(path, index=False)
    logger.info(f"Companies saved to {path}")


def generate_date_ranges(start: str, end: str, chunk_size: int = 90):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    ranges = []
    while s < e:
        ne = min(s + timedelta(days=chunk_size), e)
        ranges.append((s.strftime("%Y-%m-%d"), ne.strftime("%Y-%m-%d")))
        s = ne
    return ranges


def analyze_and_save(company: dict, start: str, end: str, outdir: str):
    ensure_dir_exists(outdir)

    outfile = os.path.join(outdir, f"historical_news_{company['ticker']}.csv")

    # If a previous run left behind an old file, remove it so we can write a fresh header
    if os.path.exists(outfile):
        os.remove(outfile)

    session = requests.Session()
    tb = TextBlobAnalyzer()
    fb = FinBertAnalyzer()
    sp = SpacySimilarityAnalyzer()
    gd = GdeltFetcher(session=session)
    news_scraper = NewspaperScraper()

    first_chunk = True
    for st, ed in generate_date_ranges(start, end):
        logger.info(f"Fetching news for {company['ticker']} from {st} to {ed}")

        arts = gd.fetch_news_for_company(company, st, ed)
        if not arts:
            continue

        df = pd.DataFrame(arts)

        # Scrape text if URL is Yahoo Finance
        def get_text(row):
            text = news_scraper.scrape(row["url"])
            return text or row.get("title", "") or ""

        df["text"] = df.apply(get_text, axis=1)
        df.drop(columns=["url", "title"], inplace=True)

        # TextBlob
        tb_res = df["text"].apply(lambda t: pd.Series(tb.analyze(t)))
        df = pd.concat([df, tb_res], axis=1)

        # FinBERT
        fb_res = df["text"].apply(lambda t: pd.Series(fb.analyze(t)))
        df = pd.concat([df, fb_res], axis=1)

        # spaCy
        df["spacy_similarity"] = df["text"].apply(
            lambda t: sp.compute_similarity(t, company["name"])
        )

        # Write out
        df.to_csv(
            outfile, index=False, mode="w" if first_chunk else "a", header=first_chunk
        )
        first_chunk = False

    logger.info(f"Saved news CSV: {outfile}")


def merge_historical_news(
    news_dir: str,
    pattern: str = "historical_news_*.csv",
    output_name: str = "historical_news_merged.csv",
):
    """
    Find all CSVs in news_dir matching `pattern`, concatenate them,
    and write a single merged CSV named `output_name` in news_dir.
    """
    ensure_dir_exists(news_dir)
    search = os.path.join(news_dir, pattern)
    files = glob.glob(search)
    if not files:
        logger.warning(f"No files found matching {search} — skipping merge.")
        return

    dfs = []
    for fp in files:
        try:
            dfs.append(pd.read_csv(fp))
        except Exception as e:
            logger.error(f"Failed to read {fp}: {e}")

    if not dfs:
        logger.warning("No valid CSVs to merge — skipping.")
        return

    merged = pd.concat(dfs, ignore_index=True)
    outpath = os.path.join(news_dir, output_name)
    merged.to_csv(outpath, index=False)
    logger.info(f"Merged CSV saved to {outpath}")
