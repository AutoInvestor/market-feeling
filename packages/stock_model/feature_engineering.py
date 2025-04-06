import pandas as pd
from stock_model.data_manager import load_from_csv, save_to_csv
from stock_model.logger import get_logger

logger = get_logger(__name__)

def engineer_features(input_path: str, output_path: str):
    """
    Reads the merged dataset, engineers new features (e.g., absolute polarity, one-hot ticker),
    handles outliers, and creates both binary and three-class targets.
    """

    df = load_from_csv(input_path)

    # ------------------------------------------------------------------------
    # 1) Outlier Handling on return_1d
    #    We clip extreme returns at the 1st and 99th percentiles.
    # ------------------------------------------------------------------------
    if 'return_1d' not in df.columns:
        logger.error("Column 'return_1d' is not found in the dataset.")
        return

    lower_clip = df['return_1d'].quantile(0.01)
    upper_clip = df['return_1d'].quantile(0.99)
    df['return_1d'] = df['return_1d'].clip(lower_clip, upper_clip)

    # ------------------------------------------------------------------------
    # 2) Create classification targets
    #    - Binary target: 1 if return_1d > 0, else 0
    #    - Three-class target:
    #        0 if return_1d < -0.0X (NEGATIVE)
    #        1 if -0.0X <= return_1d <= 0.0X (NEUTRAL)
    #        2 if return_1d >  0.0X (POSITIVE)
    #    You can adjust the neutral threshold as you like.
    # ------------------------------------------------------------------------
    df['target_binary'] = (df['return_1d'] > 0).astype(int)

    # Example: define a small region of 'neutral'
    NEGATIVE_THRESHOLD = -0.001
    POSITIVE_THRESHOLD =  0.001

    def classify_3class(r):
        if r < NEGATIVE_THRESHOLD:
            return 0  # Negative
        elif r <= POSITIVE_THRESHOLD:
            return 1  # Neutral
        else:
            return 2  # Positive

    df['target_3class'] = df['return_1d'].apply(classify_3class)

    # ------------------------------------------------------------------------
    # 3) Transform Existing Sentiment Scores
    #    - abs_polarity (absolute magnitude)
    #    - polarity_subjectivity = polarity * subjectivity
    # ------------------------------------------------------------------------
    if 'textblob_polarity' in df.columns:
        df['abs_polarity'] = df['textblob_polarity'].abs()
        df['polarity_subjectivity'] = df['textblob_polarity'] * df['textblob_subjectivity']

    # ------------------------------------------------------------------------
    # 4) One‐hot encode FinBERT label: [positive, negative, neutral]
    # ------------------------------------------------------------------------
    if 'finbert_label' in df.columns:
        finbert_dummies = pd.get_dummies(df['finbert_label'], prefix='finbert')
        df = pd.concat([df, finbert_dummies], axis=1)
        df.drop(columns=['finbert_label'], inplace=True)

    # ------------------------------------------------------------------------
    # 6) Fill spacy_similarity if missing
    # ------------------------------------------------------------------------
    if 'spacy_similarity' in df.columns:
        df['spacy_similarity'] = df['spacy_similarity'].fillna(0.0)

    # ------------------------------------------------------------------------
    # 8) Save the final feature set
    # ------------------------------------------------------------------------
    save_to_csv(df.to_dict('records'), output_path)
    logger.info(f"Feature-engineered dataset saved to {output_path}")

def main():
    input_path = './data/news_stock_dataset.csv'
    output_path = './data/final_training_data.csv'
    engineer_features(input_path, output_path)

if __name__ == "__main__":
    main()
