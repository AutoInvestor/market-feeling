# joblib_prediction_model.py
import joblib
import pandas as pd

from libs.feature_builder import build_feature_row, row_to_dataframe
from libs.finbert_analyzer import FinBertAnalyzer
from libs.newspaper_scraper import NewspaperScraper
from libs.spacy_analyzer import SpacySimilarityAnalyzer
from libs.textblob_analyzer import TextBlobAnalyzer
from stock_api.domain.prediction import Prediction
from stock_api.domain.prediction_model import PredictionModel


class JoblibPredictionModel(PredictionModel):
    def __init__(self, model_path: str):
        artefact = joblib.load(model_path)
        self._booster = artefact["model"]
        self._scaler = artefact["scaler"]
        self._columns = artefact["columns"]

        self._tb = TextBlobAnalyzer()
        self._fb = FinBertAnalyzer()
        self._sp = SpacySimilarityAnalyzer()
        self._scraper = NewspaperScraper()

    def _extract_features(self, text: str, company_name: str) -> pd.DataFrame:
        features = build_feature_row(
            {
                **self._tb.analyze(text),
                **self._fb.analyze(text),
                "spacy_similarity": self._sp.compute_similarity(text, company_name),
            }
        )
        df = row_to_dataframe(features)
        df = df[self._columns]
        df_scaled = pd.DataFrame(self._scaler.transform(df), columns=self._columns)
        return df_scaled

    def _predict(self, text: str, company_name: str) -> Prediction:
        X = self._extract_features(text, company_name)
        raw_score = self._booster.predict(X)[0]  # scalar
        return Prediction(raw_score)

    def get_prediction_from_text(self, text: str, company_name: str) -> Prediction:
        return self._predict(text, company_name)

    def get_prediction_from_url(self, url: str, company_name: str) -> Prediction:
        article_text = self._scraper.scrape(url)
        return self._predict(article_text, company_name)
