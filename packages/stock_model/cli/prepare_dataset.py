from stock_model.feature_engineer import engineer


def main():
    engineer(
        "data/historical_news_merged.csv",
        "data/historical_prices.csv",
        "data/final_training_data.csv",
    )
