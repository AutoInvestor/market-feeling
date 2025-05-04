from fastapi.testclient import TestClient
from stock_api.main import app

client = TestClient(app)


def test_post_prediction_text():
    response = client.post(
        "/prediction/text",
        json={
            "ticker": "GOOGL",
            "text": "Alphabet announces record quarterly earnings.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "feeling" in data


def test_post_prediction_url():
    response = client.post(
        "/prediction/url",
        json={
            "ticker": "AMZN",
            "url": "https://finance.yahoo.com/news/amazon-news.html",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "feeling" in data


def test_post_prediction_text_missing_fields():
    response = client.post("/prediction/text", json={"ticker": "GOOG"})
    assert response.status_code == 422


def test_post_prediction_url_invalid():
    response = client.post("/prediction/url", json={"url": "missing ticker"})
    assert response.status_code == 422
