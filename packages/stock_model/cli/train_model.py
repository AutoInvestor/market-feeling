from stock_model.trainer import train


def main():
    # Entrenar Random Forest
    train(
        "data/final_training_data.csv",
        "models/rf.joblib",
        model_name="random_forest",
        n_trials=40,
    )

    # Entrenar XGBoost
    train(
        "data/final_training_data.csv",
        "models/xgb.joblib",
        model_name="xgboost",
        n_trials=60,
    )

    # Entrenar GLM ordinal
    train("data/final_training_data.csv", "models/glm.joblib", model_name="glm_ordinal")
