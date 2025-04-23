from typing import Dict, List
import pandas as pd

FEATURE_COLUMNS: List[str] = [
    "textblob_polarity",
    "textblob_subjectivity",
    "spacy_similarity",
    "finbert_score",
    "finbert_Negative",
    "finbert_Neutral",
    "finbert_Positive",
    "polarity_x_subject",
    "abs_polarity",
    "finbert_sentiment",
]


def build_feature_row(raw: Dict[str, float | int | str | None]) -> Dict[str, float]:
    """Given the *raw* fields (some may be None), return engineered feature dict.

    Required keys in *raw* (same for CSV rows or online analyzers):
        textblob_polarity, textblob_subjectivity,
        spacy_similarity,
        finbert_label ("positive"/"negative"/"neutral"),
        finbert_score (0‑1 float)
    """

    tb_pol = float(raw.get("textblob_polarity", 0.0))
    tb_subj = float(raw.get("textblob_subjectivity", 0.0))
    sim = float(raw.get("spacy_similarity", 0.0))
    fb_lbl = (raw.get("finbert_label") or "neutral").lower()
    fb_scr = float(raw.get("finbert_score", 0.0))

    fin_neg = int(fb_lbl == "negative")
    fin_neu = int(fb_lbl == "neutral")
    fin_pos = int(fb_lbl == "positive")

    pol_x_subj = tb_pol * tb_subj
    abs_pol = abs(tb_pol)
    fin_sent = fin_pos - fin_neg

    return {
        "textblob_polarity": tb_pol,
        "textblob_subjectivity": tb_subj,
        "spacy_similarity": sim,
        "finbert_score": fb_scr,
        "finbert_Negative": fin_neg,
        "finbert_Neutral": fin_neu,
        "finbert_Positive": fin_pos,
        "polarity_x_subject": pol_x_subj,
        "abs_polarity": abs_pol,
        "finbert_sentiment": fin_sent,
    }


def row_to_dataframe(row_dict: Dict[str, float]) -> pd.DataFrame:
    return pd.DataFrame([row_dict])[FEATURE_COLUMNS]


def batch_transform(df_raw: pd.DataFrame) -> pd.DataFrame:
    finbert = pd.get_dummies(df_raw["finbert_label"], prefix="finbert").astype(int)
    for col in ["finbert_Negative", "finbert_Neutral", "finbert_Positive"]:
        if col not in finbert:
            finbert[col] = 0
    df = pd.concat([df_raw, finbert], axis=1)

    df["polarity_x_subject"] = df["textblob_polarity"] * df["textblob_subjectivity"]
    df["abs_polarity"] = df["textblob_polarity"].abs()
    df["finbert_sentiment"] = df["finbert_Positive"] - df["finbert_Negative"]

    return df[FEATURE_COLUMNS].copy()
