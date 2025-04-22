from stock_model.data_manager import load_from_csv
from stock_model.pipeline import analyze_and_save, merge_historical_news


def main():
    COMPANIES_CSV = "data/companies.csv"
    OUTDIR = "data"
    START_DATE = "2024-01-01"
    END_DATE = "2024-06-30"

    # load company list
    companies = load_from_csv(COMPANIES_CSV).to_dict("records")

    # run analysis for each company
    for c in companies:
        analyze_and_save(c, START_DATE, END_DATE, OUTDIR)

    # now merge all the per‐ticker CSVs into one
    merge_historical_news(OUTDIR)
