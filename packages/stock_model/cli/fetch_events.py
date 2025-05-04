from stock_model.data_manager import load_from_csv
from stock_model.pipeline import merge_historical_news, export_events_and_news_to_csv


def main():
    COMPANIES_CSV = "data/companies.csv"
    OUTDIR = "data"
    START_DATE = "2024-01-01"
    END_DATE = "2025-05-03"

    companies = load_from_csv(COMPANIES_CSV).to_dict("records")

    for c in companies:
        export_events_and_news_to_csv(c, START_DATE, END_DATE, OUTDIR, OUTDIR)

    merge_historical_news(OUTDIR, "news_to_import_*.csv", "news_to_import_merged.csv")
    merge_historical_news(
        OUTDIR, "events_to_import_*.csv", "events_to_import_merged.csv"
    )
