from fastapi.testclient import TestClient
from stock_api.main import app

client = TestClient(app)


def test_get_latest_news():
    response = client.get("/companies/NFLX/news/latest")
    assert response.status_code == 200
    data = response.json()
    assert {"id", "ticker", "date", "title", "url", "feeling"} <= data.keys()


def test_get_news_by_date():
    response = client.get(
        "/companies/NFLX/news?start_date=2024-04-06&end_date=2024-04-06"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for news in data:
        assert {"id", "date", "title", "url", "feeling"} <= news.keys()


def test_get_latest_news_invalid_ticker():
    response = client.get("/companies/FAKE/news/latest")
    assert response.status_code == 404


def test_get_news_by_date_invalid():
    response = client.get(
        "/companies/NFLX/news?start_date=not-a-date&end_date=2024-04-06"
    )
    assert response.status_code == 422
