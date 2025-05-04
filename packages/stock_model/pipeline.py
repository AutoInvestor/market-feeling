import joblib
import glob
import numpy as np
import uuid
import os
import pandas as pd
import requests

from datetime import timedelta, datetime
from libs.feature_builder import build_feature_row, row_to_dataframe
from stock_model.logger import get_logger
from stock_model.data_manager import ensure_dir_exists
from stock_model.fetchers.yfinance_fetcher import YFinanceFetcher
from stock_model.fetchers.gdelt_fetcher import GdeltFetcher
from libs.textblob_analyzer import TextBlobAnalyzer
from libs.finbert_analyzer import FinBertAnalyzer
from libs.spacy_analyzer import SpacySimilarityAnalyzer
from libs.newspaper_scraper import NewspaperScraper

logger = get_logger(__name__)
NASDAQ100 = [
    "AAPL",  # Apple Inc.
    "MSFT",  # Microsoft Corporation
    "AMZN",  # Amazon.com, Inc.
    "GOOGL",  # Alphabet Inc.
    "NVDA",  # NVIDIA Corporation
    "TSLA",  # Tesla, Inc.
    "NFLX",  # Netflix, Inc.
    "ADBE",  # Adobe Inc.
    "INTC",  # Intel Corporation
]


class JoblibPredictionModel:
    def __init__(self, model_path: str):
        artefact = joblib.load(model_path)
        self._booster = artefact["model"]
        self._scaler = artefact["scaler"]
        self._columns = artefact["columns"]

        self._tb = TextBlobAnalyzer()
        self._fb = FinBertAnalyzer()
        self._sp = SpacySimilarityAnalyzer()
        self._scraper = NewspaperScraper()

    def _extract_features(self, text: str, company_name: str) -> pd.DataFrame:
        features = build_feature_row(
            {
                **self._tb.analyze(text),
                **self._fb.analyze(text),
                "spacy_similarity": self._sp.compute_similarity(text, company_name),
            }
        )
        df = row_to_dataframe(features)[self._columns]
        df_scaled = pd.DataFrame(self._scaler.transform(df), columns=self._columns)
        return df_scaled

    def _predict(self, text: str, company_name: str) -> int:
        X = self._extract_features(text, company_name)
        raw_score = self._booster.predict(X)[0]
        return raw_score

    def get_prediction_from_text(self, text: str, company_name: str) -> int:
        return self._predict(text, company_name)


def make_deterministic_id(ticker: str, date: str, title: str, url: str) -> str:
    ticker_norm = ticker.upper().strip()
    date_norm = date
    title_norm = title.strip()
    url_norm = url.strip()

    raw = "||".join([ticker_norm, date_norm, title_norm, url_norm])

    return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))


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


def export_events_and_news_to_csv(
    company: dict,
    start: str,
    end: str,
    outdir_news: str,
    outdir_events: str,
):
    # ------------------------------------------------------------------ #
    # 1) Prep output paths / clean slates
    # ------------------------------------------------------------------ #
    ensure_dir_exists(outdir_news)
    ensure_dir_exists(outdir_events)

    news_path = os.path.join(outdir_news, f"news_to_import_{company['ticker']}.csv")
    events_path = os.path.join(
        outdir_events, f"events_to_import_{company['ticker']}.csv"
    )

    for p in (news_path, events_path):
        if os.path.exists(p):
            os.remove(p)

    # ------------------------------------------------------------------ #
    # 2) Initialise helpers
    # ------------------------------------------------------------------ #
    session = requests.Session()
    model = JoblibPredictionModel("models/stock_model.joblib")
    gd = GdeltFetcher(session=session)
    news_scraper = NewspaperScraper()

    first_news_chunk = True  # controls CSV header writing
    first_events_chunk = True
    version_counter = 0  # monotonically increasing per‑ticker

    # ------------------------------------------------------------------ #
    # 3) Walk the date range in 90‑day chunks
    # ------------------------------------------------------------------ #
    for st, ed in generate_date_ranges(start, end):
        logger.info("Fetching news for %s from %s to %s", company["ticker"], st, ed)

        arts = gd.fetch_news_for_company(company, st, ed)
        if not arts:
            continue

        df = pd.DataFrame(arts)

        # -------------------------------------------------------------- #
        # 3a) scrape body text (YahooFinance etc.) and run sentiment
        # -------------------------------------------------------------- #
        df["text"] = df.apply(
            lambda r: news_scraper.scrape(r["url"]) or r.get("title", "") or "",
            axis=1,
        )

        df["feeling"] = df["text"].apply(
            lambda t: int(round(model.get_prediction_from_text(t, company["name"])))
        )

        # -------------------------------------------------------------- #
        # 3b) deterministic news ID
        # -------------------------------------------------------------- #
        df["_id"] = df.apply(
            lambda r: make_deterministic_id(
                company["ticker"], r["date"], r["title"], r["url"]
            ),
            axis=1,
        )

        # -------------------------------------------------------------- #
        # 3c)  save NEWS slice
        # -------------------------------------------------------------- #
        news_cols = ["_id", "date", "ticker", "title", "url", "feeling"]
        df[news_cols].to_csv(
            news_path,
            index=False,
            mode="w" if first_news_chunk else "a",
            header=first_news_chunk,
        )
        first_news_chunk = False

        # -------------------------------------------------------------- #
        # 3d)  build & save EVENTS slice
        # -------------------------------------------------------------- #
        n_rows = len(df)
        now_iso = datetime.utcnow().isoformat(timespec="seconds")
        versions = np.arange(version_counter, version_counter + n_rows)
        version_counter += n_rows

        events_df = pd.DataFrame(
            {
                "event_id": [str(uuid.uuid4()) for _ in range(n_rows)],
                "occurred_at": now_iso,
                "aggregate_id": company["ticker"].upper(),
                "version": versions,
                "type": "ASSET_FEELING_DETECTED",
                "url": df["url"].values,
                "news_id": df["_id"].values,
                "title": df["title"].values,
                "date": df["date"].values,
                "feeling": df["feeling"].values,
            }
        )

        events_df.to_csv(
            events_path,
            index=False,
            mode="w" if first_events_chunk else "a",
            header=first_events_chunk,
        )
        first_events_chunk = False

    logger.info("Saved news CSV:   %s", news_path)
    logger.info("Saved events CSV: %s", events_path)


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


def merge_historical_news(base_dir: str, pattern: str, output_name: str):
    search = os.path.join(base_dir, pattern)
    files = glob.glob(search)
    if not files:
        logger.warning("No files found matching %s — skipping.", search)
        return

    dfs = []
    for fp in files:
        try:
            dfs.append(pd.read_csv(fp))
        except Exception as e:
            logger.error("Failed to read %s: %s", fp, e)

    if not dfs:
        logger.warning("No valid CSVs for %s — skipping.", pattern)
        return

    merged = pd.concat(dfs, ignore_index=True)

    # For convenience, sort chronologically if a date column exists
    date_col = "date" if "date" in merged.columns else "occurred_at"
    if date_col in merged.columns:
        merged.sort_values(date_col, inplace=True)

    outpath = os.path.join(base_dir, output_name)
    merged.to_csv(outpath, index=False)
    logger.info("Merged CSV saved to %s", outpath)
