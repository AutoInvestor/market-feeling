from transformers import pipeline
from stock_model.logger import get_logger

logger = get_logger(__name__)


# FINBERT:
#   finbert_label:
#       "positive", "negative", or "neutral" label indicating the primary sentiment.
#   finbert_score:
#       A probability/confidence in the assigned label, from 0.0 to 1.0.
#       Higher = more confident in the predicted label.
class FinBertAnalyzer:
    def __init__(self):
        self.pipe = pipeline(
            "sentiment-analysis",
            model="yiyanghkust/finbert-tone",
            tokenizer="yiyanghkust/finbert-tone",
            framework="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

    def analyze(self, text: str) -> dict:
        try:
            r = self.pipe(text)[0]
            return {"finbert_label": r["label"], "finbert_score": r["score"]}
        except Exception as e:
            logger.warning(f"FinBERT failed: {e}")
            return {"finbert_label": None, "finbert_score": None}
