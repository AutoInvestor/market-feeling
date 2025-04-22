import re
import pandas as pd
from stock_model.data_manager import save_to_csv
from stock_model.logger import get_logger

logger = get_logger(__name__)


def engineer(input_csv: str, output_csv: str):
    # 1) Load
    df_news = pd.read_csv(input_csv, parse_dates=["date"])
    df_prices = pd.read_csv("data/historical_prices.csv", parse_dates=["date"])

    # 2) Compute 1-day return
    df_prices.sort_values(["ticker", "date"], inplace=True)
    df_prices["return_1d"] = (
        df_prices.groupby("ticker")["close"]
        .shift(-1)
        .subtract(df_prices["close"])
        .divide(df_prices["close"])
    )

    # 3) Merge & drop missing returns
    merged = pd.merge(
        df_news,
        df_prices[["ticker", "date", "return_1d"]],
        on=["ticker", "date"],
        how="left",
    )
    before = len(merged)
    merged = merged.dropna(subset=["return_1d"])
    logger.info(f"Dropped {before - len(merged)} rows without a return_1d")

    # 4) Drop rows with invalid text
    invalid_phrases = [
        "We're unable to load stories right now.",
        "Sign in to access your portfolio",
        "Sign in",
    ]
    pattern = "|".join(map(re.escape, invalid_phrases))
    mask_bad_text = merged["text"].str.contains(pattern, na=False)
    if mask_bad_text.any():
        logger.info(f"Dropping {mask_bad_text.sum()} rows with invalid text")
        merged = merged[~mask_bad_text]

    # 5) Drop rows with out‑of‑range sentiment scores/labels
    valid_labels = {"Positive", "Negative", "Neutral"}
    mask_valid = (
        merged["textblob_polarity"].between(-1.0, 1.0)
        & merged["textblob_subjectivity"].between(0.0, 1.0)
        & merged["finbert_label"].isin(valid_labels)
        & merged["finbert_score"].between(0.0, 1.0)
        & merged["spacy_similarity"].between(0.0, 1.0)
    )
    if (~mask_valid).any():
        logger.info(
            f"Dropping {(~mask_valid).sum()} rows with invalid sentiment scores"
        )
        merged = merged[mask_valid]

    # 6) Feature engineering
    merged["abs_polarity"] = merged["textblob_polarity"].abs()
    merged["polarity_subjectivity"] = (
        merged["textblob_polarity"] * merged["textblob_subjectivity"]
    )
    finbert_dummies = pd.get_dummies(merged["finbert_label"], prefix="finbert")
    merged = pd.concat([merged, finbert_dummies], axis=1)

    # 7) Target: 11‑class 0…10 per the percentages in your image
    def cls11(r):
        if r <= -0.05:
            return 0  # ≤ -5%
        elif r <= -0.04:
            return 1  # -5% to -4%
        elif r <= -0.03:
            return 2  # -4% to -3%
        elif r <= -0.02:
            return 3  # -3% to -2%
        elif r <= -0.01:
            return 4  # -2% to -1%
        elif abs(r) <= 0.01:
            return 5  # ±1%
        elif r <= 0.02:
            return 6  # +1% to +2%
        elif r <= 0.03:
            return 7  # +2% to +3%
        elif r <= 0.04:
            return 8  # +3% to +4%
        elif r <= 0.05:
            return 9  # +4% to +5%
        else:
            return 10  # ≥ +5%

    merged["target"] = merged["return_1d"].apply(cls11)

    # 8) Keep only the columns you need for training
    cols_to_keep = [
        "abs_polarity",
        "polarity_subjectivity",
        "spacy_similarity",
        "finbert_Negative",
        "finbert_Neutral",
        "finbert_Positive",
        "target",
    ]
    final_df = merged[cols_to_keep]

    # 9) Save
    save_to_csv(final_df.to_dict("records"), output_csv)
    logger.info(f"Feature-engineered data saved to {output_csv}")
