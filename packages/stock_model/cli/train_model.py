from stock_model.trainer import train


def main():
    train("data/final_training_data.csv", "models/stock_model.joblib")
