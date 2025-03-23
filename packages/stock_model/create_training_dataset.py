import pandas as pd

def load_data(news_path, prices_path):
    news_df = pd.read_csv(news_path, parse_dates=['date'])
    prices_df = pd.read_csv(prices_path, parse_dates=['Date'])
    return news_df, prices_df

def calculate_price_changes(news_df, prices_df):
    price_changes = []

    prices_df.sort_values(['ticker', 'Date'], inplace=True)

    for idx, row in news_df.iterrows():
        ticker = row['ticker']
        pub_date = row['date']

        stock_prices = prices_df[prices_df['ticker'] == ticker]
        future_prices = stock_prices[stock_prices['Date'] >= pub_date].head(8)

        if len(future_prices) < 8:
            continue  # Skip incomplete data

        close_today = future_prices.iloc[0]['Close']
        close_1d = future_prices.iloc[1]['Close']
        close_3d = future_prices.iloc[3]['Close']
        close_7d = future_prices.iloc[7]['Close']

        price_changes.append({
            'news_id': idx,
            'pct_change_1d': (close_1d - close_today) / close_today * 100,
            'pct_change_3d': (close_3d - close_today) / close_today * 100,
            'pct_change_7d': (close_7d - close_today) / close_today * 100,
        })

    return pd.DataFrame(price_changes)

def create_final_dataset(news_df, price_changes_df):
    final_df = news_df.join(price_changes_df.set_index('news_id'), how='inner')
    final_df.dropna(inplace=True)
    return final_df

def main():
    news_path = './data/historical_news.csv'
    prices_path = './data/historical_prices.csv'
    output_path = './data/news_stock_dataset.csv'

    news_df, prices_df = load_data(news_path, prices_path)
    price_changes_df = calculate_price_changes(news_df, prices_df)
    final_df = create_final_dataset(news_df, price_changes_df)

    final_df.to_csv(output_path, index=False)
    print(f"Training dataset saved to {output_path}")

if __name__ == "__main__":
    main()
