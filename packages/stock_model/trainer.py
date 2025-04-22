import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor

from stock_model.logger import get_logger

logger = get_logger(__name__)


def wMAPE(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100


def train(
    data_csv: str, output_path: str, test_size: float = 0.3, random_state: int = 42
):
    logger.info(f"Starting training run on data: {data_csv}")
    # 1) Load
    try:
        df = pd.read_csv(data_csv)
    except Exception as e:
        logger.exception(f"Failed to read CSV {data_csv}")
        raise

    if "target" not in df.columns:
        logger.error("Expected 'target' column in training data, but it was not found")
        raise ValueError("Expected 'target' column in training data")

    X = df.drop(columns=["target"])
    y = df["target"].values
    logger.debug(f"Data loaded: {X.shape[0]} samples, {X.shape[1]} features")

    # 2) Split once
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    logger.info(
        f"Split data: train={X_train.shape[0]} rows, test={X_test.shape[0]} rows"
    )

    # 3) Define candidate models
    candidates = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(random_state=random_state),
        "Lasso": Lasso(random_state=random_state),
        "DecisionTree": DecisionTreeRegressor(random_state=random_state),
        "RandomForest": RandomForestRegressor(
            n_estimators=100, random_state=random_state
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=100, random_state=random_state
        ),
        "KNN": KNeighborsRegressor(),
    }

    results = {}
    for name, model in candidates.items():
        logger.info(f"Training model: {name}")
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = wMAPE(y_test, y_pred)
            results[name] = score
            logger.info(f"{name:17s} wMAPE: {score:6.2f}%")
        except Exception as e:
            logger.exception(f"Error training or scoring model '{name}'")
            results[name] = np.inf

    # 4) Pick best
    best_name = min(results, key=results.get)
    best_score = results[best_name]
    best_model = candidates[best_name]

    logger.info(f"Best model selected: {best_name} with wMAPE = {best_score:.2f}%")

    joblib.dump(best_model, output_path)
    logger.info(f"Saved best model '{best_name}' to {output_path}")

    return best_name, best_model, results
