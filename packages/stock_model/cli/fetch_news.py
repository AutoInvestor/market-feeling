from stock_model.data_manager import load_from_csv
from stock_model.pipeline import analyze_and_save, merge_historical_news


def main():
    COMPANIES_CSV = "data/companies.csv"
    OUTDIR = "data"
    START_DATE = "2024-01-01"
    END_DATE = "2025-05-03"

    companies = load_from_csv(COMPANIES_CSV).to_dict("records")

    for c in companies:
        analyze_and_save(c, START_DATE, END_DATE, OUTDIR)

    merge_historical_news(OUTDIR, "historical_news_*.csv", "historical_news_merged.csv")
