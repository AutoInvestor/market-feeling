import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from stock_model.logger import get_logger
from stock_model.data_manager import load_from_csv, ensure_dir_exists
from stock_model.fetchers import GdeltFetcher
from stock_model.analyzers import TextBlobAnalyzer, FinBertAnalyzer, SpacySimilarityAnalyzer

logger = get_logger(__name__)

def generate_date_ranges(start_date: str, end_date: str, chunk_size_days=90):
    """
    Generate (start, end) date pairs for smaller windows from start_date to end_date,
    each window having up to chunk_size_days days.
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    ranges = []
    while start < end:
        period_end = min(start + timedelta(days=chunk_size_days), end)
        ranges.append((start.strftime("%Y-%m-%d"), period_end.strftime("%Y-%m-%d")))
        start = period_end
    return ranges

def analyze_articles(articles, textblob_analyzer, finbert_analyzer, spacy_analyzer):
    """
    Given a list of article dicts, run all analyzers and return a DataFrame.
    """
    if not articles:
        return pd.DataFrame()

    df = pd.DataFrame(articles)

    # Prepare lists for analyzer outputs
    textblob_polarities = []
    textblob_subjectivities = []
    finbert_labels = []
    finbert_scores = []
    spacy_scores = []

    for _, row in df.iterrows():
        # Use summary if available, else use title
        text = (row.get("summary") or "").strip() or (row.get("title") or "").strip()

        # TextBlob
        tb_result = textblob_analyzer.analyze(text)
        textblob_polarities.append(tb_result["textblob_polarity"])
        textblob_subjectivities.append(tb_result["textblob_subjectivity"])

        # FinBERT
        fb_result = finbert_analyzer.analyze(text)
        finbert_labels.append(fb_result["finbert_label"])
        finbert_scores.append(fb_result["finbert_score"])

        # spaCy similarity
        sim_score = spacy_analyzer.compute_similarity(text, row.get("name", ""))
        spacy_scores.append(sim_score)

    # Append analyzer results to the DataFrame
    df["textblob_polarity"] = textblob_polarities
    df["textblob_subjectivity"] = textblob_subjectivities
    df["finbert_label"] = finbert_labels
    df["finbert_score"] = finbert_scores
    df["spacy_similarity"] = spacy_scores

    return df

def fetch_analyze_and_save_company(
    company: dict,
    start_date: str,
    end_date: str,
    base_output_dir: str,
    session: requests.Session,
    textblob_analyzer: TextBlobAnalyzer,
    finbert_analyzer: FinBertAnalyzer,
    spacy_analyzer: SpacySimilarityAnalyzer,
    chunk_size_days: int = 90
):
    """
    Fetch all date-chunks for a single company, analyze, and save to a CSV named by ticker.
    """
    ticker = company["ticker"]
    company_csv = os.path.join(base_output_dir, f"historical_news_{ticker}.csv")
    ensure_dir_exists(company_csv)

    # We'll decide whether to write the CSV header once, if the file doesn't exist
    write_header = not os.path.exists(company_csv)

    # Create the GdeltFetcher with the shared session
    gdelt_fetcher = GdeltFetcher(session=session, maxrecords=250)

    # Build chunked date windows
    date_chunks = generate_date_ranges(start_date, end_date, chunk_size_days)

    total_fetched = 0
    for chunk_start, chunk_end in date_chunks:
        logger.info(f"Fetching GDELT news for {ticker} from {chunk_start} to {chunk_end}...")
        articles = gdelt_fetcher.fetch_news_for_company(company, chunk_start, chunk_end)
        if not articles:
            continue

        # Analyze in memory
        df_chunk = analyze_articles(
            articles,
            textblob_analyzer,
            finbert_analyzer,
            spacy_analyzer
        )
        total_fetched += len(df_chunk)

        # Append to CSV
        if not df_chunk.empty:
            df_chunk.to_csv(
                company_csv,
                index=False,
                mode="a",
                header=write_header,
                encoding="utf-8"
            )
            # After the first write, do not write headers again
            if write_header:
                write_header = False

    logger.info(f"Done with {ticker}. Wrote {total_fetched} articles to {company_csv}.")

def main():
    # Input files
    companies_filepath = os.path.join("data", "companies.csv")
    base_output_dir = os.path.join("data")

    # Create the output directory if not exists
    ensure_dir_exists(base_output_dir)

    logger.info("Loading company list...")
    df_companies = load_from_csv(companies_filepath)
    if df_companies.empty:
        logger.info("No companies found. Exiting.")
        return

    companies = df_companies.to_dict(orient="records")
    logger.info(f"{len(companies)} companies loaded.")

    # Create a single requests.Session for all
    session = requests.Session()

    # Initialize analyzers (may be used by all threads)
    textblob_analyzer = TextBlobAnalyzer()
    finbert_analyzer = FinBertAnalyzer()
    spacy_analyzer = SpacySimilarityAnalyzer(model_name="en_core_web_md")

    # Global date range
    start_date = "2020-01-01"
    end_date = "2024-12-31"

    # We'll do parallel processing across companies:
    max_workers = 4  # or more, depending on your CPU/network capacity

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for company in companies:
            futures.append(
                executor.submit(
                    fetch_analyze_and_save_company,
                    company,
                    start_date,
                    end_date,
                    base_output_dir,
                    session,
                    textblob_analyzer,
                    finbert_analyzer,
                    spacy_analyzer,
                    90  # chunk_size_days
                )
            )

        # Wait for all threads to finish
        for future in as_completed(futures):
            # If there's an exception in any thread, raise it here
            future.result()

    logger.info("All companies processed. Individual CSV files written. Merging...")

    # (Optional) Merge them into one final CSV
    merged_csv_path = os.path.join(base_output_dir, "historical_news_merged.csv")
    merge_company_csvs(base_output_dir, merged_csv_path)
    logger.info(f"Merged all data into {merged_csv_path}")

def merge_company_csvs(output_dir: str, merged_csv_path: str):
    """
    Example of merging all historical_news_*.csv into a single CSV if desired.
    """
    import glob
    csv_files = glob.glob(os.path.join(output_dir, "historical_news_*.csv"))

    if not csv_files:
        logger.info("No per-company CSV files found to merge.")
        return

    df_list = []
    for f in csv_files:
        df_list.append(pd.read_csv(f, low_memory=False))

    # Simple concat; drop duplicates if necessary
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_df.drop_duplicates(subset=["url", "date"], inplace=True)

    merged_df.to_csv(merged_csv_path, index=False, encoding="utf-8")
    logger.info(f"Merged CSV saved: {merged_csv_path}")

if __name__ == "__main__":
    main()
