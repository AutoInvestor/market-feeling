from pathlib import Path
import joblib
import numpy as np
import optuna
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import statsmodels.api as sm                    # GLM ordinal
from statsmodels.miscmodels.ordinal_model import OrderedModel
from stock_model.logger import get_logger

logger = get_logger(__name__)


# ---------- 1. Métricas ----------

def _weights(y: np.ndarray) -> np.ndarray:
    return 1.0 / np.maximum(1.0, np.abs(y))


def wmape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """wMAPE en % (usa valores 0-10)."""
    return np.mean(np.abs(y_true - y_pred) * _weights(y_true)) * 100


def group_accuracy(y_true: np.ndarray, y_pred: np.ndarray, threshold: int = 5) -> float:
    """
    Accuracy binaria comparando predicción y verdad según un umbral:
    - "SELL" si < threshold
    - "BUY"  si > threshold
    Valores iguales al threshold no se incluyen en esta métrica.
    """
    true_bin = np.where(y_true < threshold, 0, np.where(y_true > threshold, 1, np.nan))
    pred_bin = np.where(y_pred < threshold, 0, np.where(y_pred > threshold, 1, np.nan))
    mask = ~np.isnan(true_bin) & ~np.isnan(pred_bin)
    return float(np.mean(true_bin[mask] == pred_bin[mask]))


def evaluate_risk_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Calcula la accuracy para los perfiles de riesgo R1–R4 según definición completa:
    - SELL es correcto si y_true <= threshold (5)
    - BUY  es correcto si y_true >= threshold (5)
    - HOLD siempre es correcto
    Se incluye HOLD en el denominador para cada perfil.
    """
    risk_ranges = {
        "R1": {"sell": list(range(0, 1)),         "hold": list(range(1, 10)),  "buy": list(range(10, 11))},
        "R2": {"sell": list(range(0, 2)),         "hold": list(range(2, 9)),   "buy": list(range(9, 11))},
        "R3": {"sell": list(range(0, 3)),         "hold": list(range(3, 8)),   "buy": list(range(8, 11))},
        "R4": {"sell": list(range(0, 4)),         "hold": list(range(4, 7)),   "buy": list(range(7, 11))},
    }

    results = {}
    for risk, ranges in risk_ranges.items():
        sell_mask = np.isin(y_pred, ranges["sell"])
        hold_mask = np.isin(y_pred, ranges["hold"])
        buy_mask  = np.isin(y_pred, ranges["buy"])

        sell_correct = sell_mask & (y_true <= 5)
        buy_correct  = buy_mask  & (y_true >= 5)
        hold_correct = hold_mask  # siempre correcto

        # Accuracy incluyendo todas las predicciones
        acc = (sell_correct.sum() + hold_correct.sum() + buy_correct.sum()) / len(y_true)
        results[risk] = acc

    return results

# ---------- 2. Métrica de preferencia acción vs mantener ----------
'''
Calcula métricas de cómo el modelo escoge entre acción (BUY/SELL) y HOLD:
- action_rate    : proporción de predicciones BUY o SELL
- hold_rate      : proporción de predicciones HOLD
- action_accuracy: accuracy de las predicciones BUY/SELL (correctas según threshold)
- hold_accuracy  : accuracy de HOLD (si se considera correcto cuando y_true == threshold)
'''
def action_preference_metrics(y_true: np.ndarray, y_pred: np.ndarray, threshold: int = 5) -> dict:
    sell_mask = y_pred < threshold
    buy_mask  = y_pred > threshold
    hold_mask = y_pred == threshold

    action_mask = sell_mask | buy_mask

    # Proporciones
    action_rate = float(np.mean(action_mask))
    hold_rate   = float(np.mean(hold_mask))

    # Precisión de acción
    action_correct = (sell_mask & (y_true <= threshold)) | (buy_mask & (y_true >= threshold))
    action_accuracy = float(np.sum(action_correct & action_mask) / action_mask.sum()) if action_mask.sum() > 0 else float('nan')

    # Precisión de HOLD
    hold_correct = hold_mask & (y_true == threshold)
    hold_accuracy = float(np.sum(hold_correct) / hold_mask.sum()) if hold_mask.sum() > 0 else float('nan')

    return {
        'action_rate': action_rate,
        'hold_rate': hold_rate,
        'action_accuracy': action_accuracy,
        'hold_accuracy': hold_accuracy,
    }

# ---------- 2. Model wrappers ---------- Model wrappers ----------

def _fit_glm_ordinal(X_tr: pd.DataFrame, y_tr: pd.Series) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Ajusta un modelo ordinal con distribución logit. No añadimos const explícita;
    OrderedModel añade internamente los umbrales.
    """
    model = OrderedModel(
        endog=y_tr,
        exog=X_tr,
        distr="logit",
    )
    res = model.fit(method="bfgs", disp=False)
    return res


def _predict_glm_ordinal(model: sm.regression.linear_model.RegressionResultsWrapper, X: pd.DataFrame) -> np.ndarray:
    """
    Predice la categoría con mayor probabilidad.
    """
    probs = model.model.predict(model.params, exog=X)
    return probs.argmax(axis=1)


def _get_model_and_space(model_name: str):
    if model_name == "random_forest":
        Model = RandomForestClassifier
        space = {
            "n_estimators": lambda t: t.suggest_int("n_estimators", 200, 800, step=100),
            "max_depth":   lambda t: t.suggest_int("max_depth", 3, 15),
            "min_samples_leaf": lambda t: t.suggest_int("min_samples_leaf", 1, 5),
        }
    elif model_name == "xgboost":
        Model = XGBClassifier
        space = {
            "learning_rate": lambda t: t.suggest_float("lr", 0.01, 0.2, log=True),
            "max_depth":     lambda t: t.suggest_int("max_depth", 3, 10),
            "n_estimators":  lambda t: t.suggest_int("n_estimators", 300, 1200, step=100),
            "subsample":     lambda t: t.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": lambda t: t.suggest_float("colsample", 0.5, 1.0),
        }
    else:
        raise ValueError("Modelo no soportado: {model_name}")
    return Model, space


# ---------- 3. Objetivo Optuna ----------

def _objective(trial, X: pd.DataFrame, y: pd.Series, cv: StratifiedKFold, model_name: str) -> float:
    if model_name == "glm_ordinal":
        oof = np.zeros(len(y), dtype=int)
        for tr_idx, val_idx in cv.split(X, y):
            X_tr, y_tr = X.iloc[tr_idx], y.iloc[tr_idx]
            mod = _fit_glm_ordinal(X_tr, y_tr)
            oof[val_idx] = _predict_glm_ordinal(mod, X.iloc[val_idx])
        return wmape(y.to_numpy(), oof)
    else:
        Model, space = _get_model_and_space(model_name)
        params = {k: f(trial) for k, f in space.items()}
        params["random_state"] = 42
        oof = np.zeros(len(y), dtype=int)
        for tr_idx, val_idx in cv.split(X, y):
            mdl = Model(**params)
            mdl.fit(X.iloc[tr_idx], y.iloc[tr_idx])
            oof[val_idx] = mdl.predict(X.iloc[val_idx])
        return wmape(y.to_numpy(), oof)


# ---------- 4. Entrenamiento general ----------

def train(
    data_csv: str,
    model_path: str,
    model_name: str = "glm_ordinal",
    n_trials: int = 30,
):
    logger.info(f"Entrenando modelo {model_name}...")
    df = pd.read_csv(data_csv)
    X = df.drop(columns=["target"])
    y = df["target"].astype(int)

    # Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Escalado: preservamos índices para alinear exog/endog
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X.columns,
        index=X_train.index
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X.columns,
        index=X_test.index
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # Optimización
    if model_name == "glm_ordinal":
        study_best = _objective(None, X_train_scaled, y_train, cv, model_name)
        final_model = _fit_glm_ordinal(X_train_scaled, y_train)
    else:
        study = optuna.create_study(direction="minimize")
        study.optimize(
            lambda t: _objective(t, X_train_scaled, y_train, cv, model_name),
            n_trials=n_trials, show_progress_bar=True
        )
        best_params, study_best = study.best_params, study.best_value
        Model, _ = _get_model_and_space(model_name)
        final_model = Model(**{**best_params, "random_state": 42})
        final_model.fit(X_train_scaled, y_train)

    logger.info(f"Mejor wMAPE CV (sobre train): {study_best:.3f}%")

    # Predicción en test
    if model_name == "glm_ordinal":
        preds_test = _predict_glm_ordinal(final_model, X_test_scaled)
    else:
        preds_test = final_model.predict(X_test_scaled)

    # Métricas básicas
    acc_real  = accuracy_score(y_test, preds_test)
    acc_group = group_accuracy(y_test.to_numpy(), preds_test, threshold=5)
    wm        = wmape(y_test.to_numpy(), preds_test)
    logger.info(f"[Test] Accuracy exacta            : {acc_real:.3%}")
    logger.info(f"[Test] Accuracy sell vs buy grupos: {acc_group:.3%}")
    logger.info(f"[Test] wMAPE completo             : {wm:.3f}%")

    # Métricas por perfil de riesgo
    risk_metrics = evaluate_risk_accuracy(y_test.to_numpy(), preds_test)
    for r, val in risk_metrics.items():
        logger.info(f"[Test] Accuracy {r}               : {val:.3%}")

        # Métrica de preferencia acción vs mantener
    pref_metrics = action_preference_metrics(y_test.to_numpy(), preds_test, threshold=5)
    logger.info(f"[Test] Action rate                : {pref_metrics['action_rate']:.3%}")
    logger.info(f"[Test] Hold rate                  : {pref_metrics['hold_rate']:.3%}")
    logger.info(f"[Test] Action accuracy            : {pref_metrics['action_accuracy']:.3%}")
    logger.info(f"[Test] Hold accuracy              : {pref_metrics['hold_accuracy']:.3%}")

# Guardado
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": final_model,
        "scaler": scaler,
        "columns": X.columns.tolist(),
        "model_name": model_name,
        "threshold": 5,
    }, model_path)
    logger.info(f"Modelo guardado → {model_path}")
