# Fetch only company overviews
python -m stock_model.main --steps fetch_companies

# Fetch news
python -m stock_model.main --steps fetch_news

# Fetch prices
python -m stock_model.main --steps fetch_prices

# Prepare dataset
python -m stock_model.main --steps prepare_dataset

# Train model
python -m stock_model.main --steps train_model
