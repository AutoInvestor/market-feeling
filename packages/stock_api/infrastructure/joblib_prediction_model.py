import joblib
import pandas as pd

from libs.feature_builder import build_feature_row, row_to_dataframe
from libs.finbert_analyzer import FinBertAnalyzer
from libs.newspaper_scraper import NewspaperScraper
from libs.spacy_analyzer import SpacySimilarityAnalyzer
from libs.textblob_analyzer import TextBlobAnalyzer
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.raw_feeling import RawFeeling
from stock_api.logger import get_logger

logger = get_logger(__name__)


class JoblibPredictionModel(PredictionModel):
    def __init__(self, model_path: str):
        logger.info("Loading prediction model from %s", model_path)
        artefact = joblib.load(model_path)
        self._booster = artefact["model"]
        self._scaler = artefact["scaler"]
        self._columns = artefact["columns"]
        logger.debug(
            "Model loaded: booster=%r, scaler=%r, %d feature columns",
            self._booster,
            self._scaler,
            len(self._columns),
        )

        self._tb = TextBlobAnalyzer()
        self._fb = FinBertAnalyzer()
        self._sp = SpacySimilarityAnalyzer()
        self._scraper = NewspaperScraper()
        logger.info("Text analyzers initialized")

    def _extract_features(self, text: str, company_name: str) -> pd.DataFrame:
        logger.debug("Extracting features for company '%s'", company_name)
        features = build_feature_row(
            {
                **self._tb.analyze(text),
                **self._fb.analyze(text),
                "spacy_similarity": self._sp.compute_similarity(text, company_name),
            }
        )
        df = row_to_dataframe(features)[self._columns]
        df_scaled = pd.DataFrame(self._scaler.transform(df), columns=self._columns)
        logger.debug(
            "Extracted and scaled features: %s", df_scaled.to_dict(orient="records")
        )
        return df_scaled

    def _predict(self, text: str, company_name: str) -> RawFeeling:
        logger.info("Running prediction for company '%s'", company_name)
        X = self._extract_features(text, company_name)
        raw_feeling = self._booster.predict(X)[0]
        logger.info("Model output raw feeling=%s", raw_feeling)
        return RawFeeling(raw_feeling)

    def get_prediction_from_text(self, text: str, company_name: str) -> RawFeeling:
        logger.debug("get_prediction_from_text called for %s", company_name)
        return self._predict(text, company_name)

    def get_prediction_from_url(self, url: str, company_name: str) -> RawFeeling:
        logger.debug(
            "get_prediction_from_url called for %s (url=%s)", company_name, url
        )
        article_text = self._scraper.scrape(url)
        logger.debug("Scraped %d characters of article text", len(article_text))
        return self._predict(article_text, company_name)
