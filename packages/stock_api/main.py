from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import requests
import os

# Import functions or classes from the model package
from stock_model.train.train_model import load_data, train_model

app = FastAPI()

# Load the pre-trained model using the local package
try:
    model_path = os.path.join("models", "stock_model.pkl")
    model = joblib.load(model_path)
except Exception as e:
    model = None
    print("Model not found. Ensure you have built it using the model project.")

@app.get("/companies")
def get_companies():
    try:
        companies_path = os.path.join("data", "companies.csv")
        df = pd.read_csv(companies_path)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error loading companies data.")

@app.get("/realtime/{ticker}")
def get_realtime_data(ticker: str):
    API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "your_api_key_here")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("Global Quote", {})
        if not data:
            raise HTTPException(status_code=404, detail="Ticker data not found.")
        return data
    else:
        raise HTTPException(status_code=500, detail="Error fetching data from external API.")

@app.post("/predict")
def predict_stock(features: dict):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not available. Train the model first.")
    try:
        input_df = pd.DataFrame([features])
        prediction = model.predict(input_df.select_dtypes(include=["number"]))
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid input data for prediction.")
