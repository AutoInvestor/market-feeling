from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import optuna
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from stock_model.logger import get_logger

logger = get_logger(__name__)


def _weights(y: np.ndarray) -> np.ndarray:
    """Sample weights that make MAE ≈ wMAPE (1 / max(1, |y|))."""
    return 1.0 / np.maximum(1.0, np.abs(y))


def wmape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return np.mean(np.abs(y_true - y_pred) * _weights(y_true)) * 100


def lgbm_wmape(preds: np.ndarray, dataset: lgb.Dataset):
    y_true = dataset.get_label()
    score = wmape(y_true, np.rint(preds))
    return "wMAPE", score, False  # lower is better


def _objective(trial: optuna.Trial, X: pd.DataFrame, y: pd.Series, cv: StratifiedKFold):
    params = {
        "objective": "regression_l1",  # MAE
        "metric": "None",  # we'll use custom metric
        "learning_rate": trial.suggest_float("lr", 0.01, 0.1, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 15, 63, step=2),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.6, 1.0),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.6, 1.0),
        "bagging_freq": trial.suggest_int("bagging_freq", 1, 8),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 60),
        "lambda_l1": trial.suggest_float("lambda_l1", 0.0, 5.0),
        "lambda_l2": trial.suggest_float("lambda_l2", 0.0, 5.0),
        "verbosity": -1,
        "seed": 42,
    }

    oof = np.zeros(len(y))
    for tr_idx, val_idx in cv.split(X, y):
        w_tr = _weights(y.iloc[tr_idx])
        w_val = _weights(y.iloc[val_idx])

        booster = lgb.train(
            params,
            lgb.Dataset(X.iloc[tr_idx], y.iloc[tr_idx], weight=w_tr),
            num_boost_round=4000,
            valid_sets=[lgb.Dataset(X.iloc[val_idx], y.iloc[val_idx], weight=w_val)],
            callbacks=[
                lgb.early_stopping(200, verbose=False),
                lgb.log_evaluation(period=0),
            ],
            feval=lgbm_wmape,
        )
        oof[val_idx] = booster.predict(X.iloc[val_idx])

    return wmape(y, oof)


def train(data_csv: str, model_path: str, n_trials: int = 50):
    logger.info("Training model (wMAPE‑optimised) ...")
    df = pd.read_csv(data_csv)
    X = df.drop(columns=["target"])
    y = df["target"].astype(int)

    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    study = optuna.create_study(direction="minimize")
    study.optimize(
        lambda t: _objective(t, X_scaled, y, cv),
        n_trials=n_trials,
        show_progress_bar=True,
    )

    logger.info(f"Best CV wMAPE: {study.best_value:.3f}%")

    # retrain on full data with best params & weights
    best_params = {
        **study.best_params,
        "objective": "regression_l1",
        "metric": "None",
        "verbosity": -1,
        "seed": 42,
    }
    full_weights = _weights(y)
    booster = lgb.train(
        best_params,
        lgb.Dataset(X_scaled, y, weight=full_weights),
        num_boost_round=int(
            1.1 * booster.best_iteration
            if (booster := study.best_trial.user_attrs.get("booster"))
            else 1500
        ),
        feval=lgbm_wmape,
        callbacks=[lgb.log_evaluation(period=100)],
    )

    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": booster, "scaler": scaler, "columns": X.columns.tolist()}, model_path
    )
    logger.info(f"Model saved → {model_path}")
