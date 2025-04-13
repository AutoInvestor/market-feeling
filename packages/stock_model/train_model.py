import pandas as pd
from stock_model.data_manager import load_from_csv
from stock_model.logger import get_logger

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# For up/down sampling
from sklearn.utils import resample

# or install imbalanced-learn: from imblearn.over_sampling import RandomOverSampler
# or from imblearn.under_sampling import RandomUnderSampler

logger = get_logger(__name__)


def sample_data(X, y, strategy="none"):
    """
    Applies up-sampling or down-sampling to address class imbalance.
    :param X: Feature matrix
    :param y: Series of labels
    :param strategy: 'none', 'up', or 'down'
    :return: (X_resampled, y_resampled)
    """
    df_temp = pd.concat([X, y], axis=1)

    if strategy == "up":
        # Up-sample the minority class
        major_class = df_temp[y == y.value_counts().idxmax()]
        minor_class = df_temp[y == y.value_counts().idxmin()]

        n_major = len(major_class)
        n_minor = len(minor_class)

        # If there's more than 1 minority class, pick the smallest class
        # But here we assume binary for upsampling.
        # For multi-class you'd up-sample each minority class individually
        minor_class_upsampled = resample(
            minor_class, replace=True, n_samples=n_major, random_state=42
        )
        df_resampled = pd.concat([major_class, minor_class_upsampled])
        logger.info(f"Up-sampled from {len(df_temp)} to {len(df_resampled)}")
        X_resampled = df_resampled.drop(columns=y.name)
        y_resampled = df_resampled[y.name]

    elif strategy == "down":
        # Down-sample the majority class
        major_class = df_temp[y == y.value_counts().idxmax()]
        minor_class = df_temp[y == y.value_counts().idxmin()]

        n_major = len(major_class)
        n_minor = len(minor_class)

        major_class_downsampled = resample(
            major_class, replace=False, n_samples=n_minor, random_state=42
        )
        df_resampled = pd.concat([major_class_downsampled, minor_class])
        logger.info(f"Down-sampled from {len(df_temp)} to {len(df_resampled)}")
        X_resampled = df_resampled.drop(columns=y.name)
        y_resampled = df_resampled[y.name]

    else:
        # No sampling
        X_resampled, y_resampled = X, y

    return X_resampled, y_resampled


def train_and_evaluate(X, y, problem_name="Binary", sampling="none"):
    """
    Trains a Random Forest and Logistic Regression on the given data (X, y),
    optionally applying up/down sampling. Then prints accuracy & classification report.
    """
    # ------------------------------------------------------------------------
    # 1) (Optional) sampling
    # ------------------------------------------------------------------------
    X_res, y_res = sample_data(X, y, strategy=sampling)

    # ------------------------------------------------------------------------
    # 2) Train/Test Split
    # ------------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=42, stratify=y_res
    )

    # ------------------------------------------------------------------------
    # 3) Random Forest (initial)
    # ------------------------------------------------------------------------
    logger.info(f"\n--- {problem_name} - RandomForest ({sampling}-sampling) ---")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    rf_preds = rf_model.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    logger.info(f"RandomForest Accuracy: {rf_acc:.2f}")
    logger.info(
        "RandomForest Classification Report:\n"
        + classification_report(y_test, rf_preds)
    )

    # ------------------------------------------------------------------------
    # 4) Hyperparameter Tuning (optional)
    # ------------------------------------------------------------------------
    logger.info("Starting RandomForest hyperparameter tuning...")
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [5, 10, None],
        "min_samples_split": [2, 5],
    }

    grid = GridSearchCV(
        RandomForestClassifier(class_weight="balanced", random_state=42),
        param_grid=param_grid,
        cv=3,
        scoring="accuracy",
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)

    best_rf = grid.best_estimator_
    best_rf_preds = best_rf.predict(X_test)
    best_rf_acc = accuracy_score(y_test, best_rf_preds)
    logger.info(f"Best RF Params: {grid.best_params_}")
    logger.info(f"Tuned RF Accuracy: {best_rf_acc:.2f}")
    logger.info(
        "Tuned RF Classification Report:\n"
        + classification_report(y_test, best_rf_preds)
    )

    # ------------------------------------------------------------------------
    # 5) Logistic Regression
    # ------------------------------------------------------------------------
    logger.info(f"\n--- {problem_name} - LogisticRegression ({sampling}-sampling) ---")
    # For multi-class, "multinomial" solver is often good
    if len(y.unique()) > 2:
        lr = LogisticRegression(
            multi_class="multinomial", solver="lbfgs", max_iter=1000
        )
    else:
        lr = LogisticRegression(solver="lbfgs", max_iter=1000)
    lr.fit(X_train, y_train)

    lr_preds = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    logger.info(f"LogisticRegression Accuracy: {lr_acc:.2f}")
    logger.info(
        "LogisticRegression Classification Report:\n"
        + classification_report(y_test, lr_preds)
    )


def train_model(data_path: str):
    """
    Loads features from CSV and trains multiple classification models:
    - Binary classification (target_binary)
    - Three-class classification (target_3class)
    With or without up/down sampling, comparing RandomForest & LogisticRegression.
    """

    df = load_from_csv(data_path)
    # Columns potentially in the dataset after feature engineering
    candidate_features = [
        "textblob_polarity",
        "textblob_subjectivity",
        "abs_polarity",
        "polarity_subjectivity",
        "finbert_score",
        "spacy_similarity",
        "finbert_positive",
        "finbert_negative",
        "finbert_neutral",
    ]
    # Plus any 'ticker_' columns from one-hot encoding
    ticker_cols = [col for col in df.columns if col.startswith("ticker_")]

    features = [feat for feat in candidate_features if feat in df.columns]
    features += ticker_cols  # add all the one-hot ticker columns

    # Check for the two targets
    if "target_binary" not in df.columns:
        logger.error(
            "No 'target_binary' column found. Please run feature engineering first."
        )
        return
    if "target_3class" not in df.columns:
        logger.error(
            "No 'target_3class' column found. Please run feature engineering first."
        )
        return

    # Prepare data
    X = df[features].fillna(0.0)

    # ------------------------------------------------------------------------
    # 1) Train on BINARY classification
    # ------------------------------------------------------------------------
    y_bin = df["target_binary"]

    # We'll try no sampling, up-sampling, and down-sampling
    for sampling_method in ["none", "up", "down"]:
        train_and_evaluate(X, y_bin, problem_name="Binary", sampling=sampling_method)

    # ------------------------------------------------------------------------
    # 2) Train on THREE-CLASS classification
    # ------------------------------------------------------------------------
    y_3class = df["target_3class"]

    for sampling_method in ["none", "up", "down"]:
        train_and_evaluate(
            X, y_3class, problem_name="3-Class", sampling=sampling_method
        )


def main():
    data_path = "./data/final_training_data.csv"
    train_model(data_path)


if __name__ == "__main__":
    main()
