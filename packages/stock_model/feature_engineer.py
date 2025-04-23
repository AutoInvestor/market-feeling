import re

import numpy as np
import pandas as pd

from libs.feature_builder import batch_transform
from stock_model.logger import get_logger

logger = get_logger(__name__)


def engineer(news_csv: str, prices_csv: str, output_csv: str) -> None:
    logger.info("Starting feature engineering …")

    df_news = pd.read_csv(news_csv, parse_dates=["date"])
    df_prices = pd.read_csv(prices_csv, parse_dates=["date"])

    # 1. One-day forward return
    df_prices.sort_values(["ticker", "date"], inplace=True)
    df_prices["return_1d"] = (
        df_prices.groupby("ticker")["close"].shift(-1) - df_prices["close"]
    ) / df_prices["close"]

    # 2. Merge and keep rows that have a future close price
    merged = df_news.merge(
        df_prices[["ticker", "date", "return_1d"]], on=["ticker", "date"], how="left"
    ).dropna(subset=["return_1d"])

    # 3. Remove Yahoo placeholder rows (“Sign in” etc.)
    bad_phrases = [
        "We're unable to load stories right now.",
        "Sign in to access your portfolio",
        "Sign in",
    ]
    merged = merged[
        ~merged["text"].str.contains("|".join(map(re.escape, bad_phrases)), na=False)
    ]

    # 4. Sentiment sanity-check ranges
    ok = (
        merged["textblob_polarity"].between(-1, 1)
        & merged["textblob_subjectivity"].between(0, 1)
        & merged["finbert_score"].between(0, 1)
        & merged["spacy_similarity"].between(0, 1)
    )
    merged = merged[ok]

    # 5. Build feature matrix (handled by the shared helper)
    feat_df = batch_transform(merged)

    # 6. Target: 11-class ordinal bucketing
    thresholds = np.array(
        [-0.025, -0.02, -0.015, -0.01, -0.005, 0.005, 0.01, 0.015, 0.02, 0.025]
    )
    feat_df["target"] = np.searchsorted(
        thresholds, merged["return_1d"].values, side="right"
    )

    # 7. Save to disk
    feat_df.to_csv(output_csv, index=False)
    logger.info(
        f"Feature-engineered CSV written to {output_csv}  ({len(feat_df)} rows)"
    )
