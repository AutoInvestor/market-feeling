import pandas as pd

def categorize_change(value, threshold=1.0):
    if value > threshold:
        return 'positive'
    elif value < -threshold:
        return 'negative'
    else:
        return 'neutral'

def engineer_features(df):
    df['finbert_positive'] = (df['finbert_label'] == 'positive').astype(int)
    df['finbert_negative'] = (df['finbert_label'] == 'negative').astype(int)
    df['finbert_neutral'] = (df['finbert_label'] == 'neutral').astype(int)

    df['strong_sentiment'] = ((df['textblob_polarity'].abs() > 0.5) |
                              (df['finbert_score'] > 0.8)).astype(int)

    # Interaction feature
    df['polarity_subjectivity'] = df['textblob_polarity'] * df['textblob_subjectivity']

    # Categorize targets
    df['target_1d'] = df['pct_change_1d'].apply(categorize_change)
    df['target_3d'] = df['pct_change_3d'].apply(categorize_change)
    df['target_7d'] = df['pct_change_7d'].apply(categorize_change)

    features = [
        'textblob_polarity', 'textblob_subjectivity', 'finbert_positive',
        'finbert_negative', 'finbert_neutral', 'finbert_score',
        'spacy_similarity', 'strong_sentiment', 'polarity_subjectivity'
    ]

    return df[features + ['target_1d', 'target_3d', 'target_7d']]

def main():
    dataset_path = './data/news_stock_dataset.csv'
    output_path = './data/final_training_data.csv'

    df = pd.read_csv(dataset_path)
    final_df = engineer_features(df)
    final_df.to_csv(output_path, index=False)
    print(f"Feature-engineered dataset saved to {output_path}")

if __name__ == "__main__":
    main()
