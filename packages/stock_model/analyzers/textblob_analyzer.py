from textblob import TextBlob


class TextBlobAnalyzer:
    @staticmethod
    def analyze(text: str) -> dict:
        b = TextBlob(text)
        return {
            "textblob_polarity": b.sentiment.polarity,
            "textblob_subjectivity": b.sentiment.subjectivity,
        }
