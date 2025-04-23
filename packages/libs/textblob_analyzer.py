from textblob import TextBlob


# TEXTBLOB:
#   textblob_polarity:
#       Ranges from -1.0 (very negative) to +1.0 (very positive).
#       e.g. +0.6 = somewhat positive sentiment.
#   textblob_subjectivity:
#       Ranges from 0.0 (highly objective) to 1.0 (highly subjective).
#       e.g. 0.9 = mostly opinion-based content.
class TextBlobAnalyzer:
    @staticmethod
    def analyze(text: str) -> dict:
        b = TextBlob(text)
        return {
            "textblob_polarity": b.sentiment.polarity,
            "textblob_subjectivity": b.sentiment.subjectivity,
        }
