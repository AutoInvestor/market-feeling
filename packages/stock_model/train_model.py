import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score

def train_and_evaluate(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print("Classification Report:")
    print(classification_report(y_test, preds))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))

    scores = cross_val_score(model, X, y, cv=5, scoring='f1_weighted')
    print(f"Cross-validated Weighted F1-score: {scores.mean():.4f}")

def main():
    data_path = './data/final_training_data.csv'
    df = pd.read_csv(data_path)

    features = [
        'textblob_polarity', 'textblob_subjectivity', 'finbert_positive',
        'finbert_negative', 'finbert_neutral', 'finbert_score',
        'spacy_similarity', 'strong_sentiment', 'polarity_subjectivity'
    ]

    print("Training model for 1-day stock reaction...")
    train_and_evaluate(df[features], df['target_1d'])

    print("\nTraining model for 3-day stock reaction...")
    train_and_evaluate(df[features], df['target_3d'])

    print("\nTraining model for 7-day stock reaction...")
    train_and_evaluate(df[features], df['target_7d'])

if __name__ == "__main__":
    main()
