import warnings
import spacy
from stock_model.logger import get_logger

logger = get_logger(__name__)

# Suppress spaCy W008 warnings about empty vectors
warnings.filterwarnings(
    "ignore", message=r"\[W008\] Evaluating Doc\.similarity based on empty vectors\."
)


class SpacySimilarityAnalyzer:
    def __init__(self, model: str = "en_core_web_md"):
        try:
            self.nlp = spacy.load(model)
        except Exception as e:
            logger.error(f"Failed to load spaCy model '{model}': {e}")
            raise

    def compute_similarity(self, t1: str, t2: str) -> float:
        """
        Compute semantic similarity between two text strings using spaCy vectors.

        Returns a float between 0.0 and 1.0. If either document lacks vectors, returns 0.0.
        """
        try:
            doc1 = self.nlp(t1)
            doc2 = self.nlp(t2)
            # If either doc has no vectors, similarity is unreliable
            if not doc1.has_vector or not doc2.has_vector:
                return 0.0
            return doc1.similarity(doc2)
        except Exception as e:
            logger.warning(f"spaCy similarity computation failed: {e}")
            return 0.0
