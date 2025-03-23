from textblob import TextBlob
from transformers import pipeline
import spacy
from stock_model.logger import get_logger

logger = get_logger(__name__)

##############################
# ANALYZER SCORES EXPLAINED
##############################
# TEXTBLOB:
#   textblob_polarity:
#       Ranges from -1.0 (very negative) to +1.0 (very positive).
#       e.g. +0.6 = somewhat positive sentiment.
#   textblob_subjectivity:
#       Ranges from 0.0 (highly objective) to 1.0 (highly subjective).
#       e.g. 0.9 = mostly opinion-based content.

# FINBERT:
#   finbert_label:
#       "positive", "negative", or "neutral" label indicating the primary sentiment.
#   finbert_score:
#       A probability/confidence in the assigned label, from 0.0 to 1.0.
#       Higher = more confident in the predicted label.

# SPACY:
#   spacy_similarity:
#       Ranges from 0.0 (no similarity) to 1.0 (highly similar).
#       Measures how similar the article text is to the company name based on spaCy embeddings.

class TextBlobAnalyzer:
    """
    Analyzes sentiment using TextBlob (polarity and subjectivity).
    """

    @staticmethod
    def analyze(text: str) -> dict:
        blob = TextBlob(text)
        return {
            "textblob_polarity": blob.sentiment.polarity,
            "textblob_subjectivity": blob.sentiment.subjectivity,
        }


class FinBertAnalyzer:
    """
    Analyzes sentiment using FinBERT from Hugging Face transformers.
    """

    def __init__(self):
        self._pipeline = pipeline(
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
            result = self._pipeline(text)[0]
            return {
                "finbert_label": result["label"],
                "finbert_score": result["score"],
            }
        except Exception as e:
            logger.warning(f"FinBERT analysis failed for text '{text[:30]}...': {e}")
            return {
                "finbert_label": None,
                "finbert_score": None,
            }


class SpacySimilarityAnalyzer:
    """
    Computes similarity between two texts using a spaCy model.
    """

    def __init__(self, model_name="en_core_web_md"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError as e:
            logger.error(f"Failed to load spaCy model '{model_name}'. Make sure it's installed. {e}")
            raise

    def compute_similarity(self, text1: str, text2: str) -> float:
        try:
            doc1 = self.nlp(text1)
            doc2 = self.nlp(text2)
            return doc1.similarity(doc2)
        except Exception as e:
            logger.warning(f"spaCy similarity computation failed: {e}")
            return 0.0
