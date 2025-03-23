import os
import pandas as pd
from stock_model.logger import get_logger
from stock_model.data_manager import load_from_csv, ensure_dir_exists
from stock_model.fetchers import GdeltFetcher
from stock_model.analyzers import TextBlobAnalyzer, FinBertAnalyzer, SpacySimilarityAnalyzer

logger = get_logger(__name__)

def main():
    companies_filepath = os.path.join("data", "companies.csv")
    output_filepath = os.path.join("data", "historical_news.csv")
    ensure_dir_exists(output_filepath)

    logger.info("Loading company list...")
    df_companies = load_from_csv(companies_filepath)
    if df_companies.empty:
        logger.info("No companies found. Exiting.")
        return

    companies = df_companies.to_dict(orient="records")
    logger.info(f"{len(companies)} companies loaded.")

    # Initialize GDELT fetcher & analyzers
    gdelt_fetcher = GdeltFetcher(timespan="3m", maxrecords=250)
    textblob_analyzer = TextBlobAnalyzer()
    finbert_analyzer = FinBertAnalyzer()
    spacy_analyzer = SpacySimilarityAnalyzer(model_name="en_core_web_md")

    all_news = []
    # Fetch news for each company
    for i, company in enumerate(companies, start=1):
        logger.info(f"({i}/{len(companies)}) Fetching news for {company['name']} ({company['ticker']}).")
        articles = gdelt_fetcher.fetch_news_for_company(company)
        if articles:
            all_news.extend(articles)

    logger.info(f"Total articles fetched: {len(all_news)}.")
    if not all_news:
        logger.info("No articles fetched. Nothing to analyze or save.")
        return

    df_news = pd.DataFrame(all_news)

    # Analyze each article
    textblob_polarities = []
    textblob_subjectivities = []
    finbert_labels = []
    finbert_scores = []
    spacy_scores = []

    for _, row in df_news.iterrows():
        # Use summary if available, else use title
        text = row["summary"].strip() or row["title"].strip()

        # TextBlob
        tb_result = textblob_analyzer.analyze(text)
        textblob_polarities.append(tb_result["textblob_polarity"])
        textblob_subjectivities.append(tb_result["textblob_subjectivity"])

        # FinBERT
        fb_result = finbert_analyzer.analyze(text)
        finbert_labels.append(fb_result["finbert_label"])
        finbert_scores.append(fb_result["finbert_score"])

        # spaCy similarity
        sim_score = spacy_analyzer.compute_similarity(text, row["name"])
        spacy_scores.append(sim_score)

    df_news["textblob_polarity"] = textblob_polarities
    df_news["textblob_subjectivity"] = textblob_subjectivities
    df_news["finbert_label"] = finbert_labels
    df_news["finbert_score"] = finbert_scores
    df_news["spacy_similarity"] = spacy_scores

    # Save to CSV
    df_news.to_csv(output_filepath, index=False, encoding="utf-8")
    logger.info(f"News data + sentiments saved to {output_filepath}")

if __name__ == "__main__":
    main()
