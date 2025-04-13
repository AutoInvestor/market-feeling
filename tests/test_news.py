from fastapi.testclient import TestClient
from stock_api.main import app

client = TestClient(app)


def test_get_latest_news():
    response = client.get("/companies/NFLX/news/latest")
    assert response.status_code == 200
    data = response.json()
    assert {"id", "ticker", "date", "title", "url", "prediction"} <= data.keys()
    assert {"score", "interpretation", "percentage_range"} <= data["prediction"].keys()


def test_get_news_by_date():
    response = client.get("/companies/NFLX/news?date=2024-04-06")
    assert response.status_code == 200
    data = response.json()
    assert "news" in data and isinstance(data["news"], list)
    for news in data["news"]:
        assert {"id", "date", "title", "url", "prediction"} <= news.keys()
        assert {"score", "interpretation", "percentage_range"} <= news[
            "prediction"
        ].keys()


def test_get_latest_news_invalid_ticker():
    # response = client.get("/companies/FAKE/news/latest")
    # assert response.status_code == 404
    pass


def test_get_news_by_date_invalid():
    response = client.get("/companies/NFLX/news?date=not-a-date")
    assert response.status_code == 422
