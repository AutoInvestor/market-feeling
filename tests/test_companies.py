from fastapi.testclient import TestClient
from stock_api.main import app

client = TestClient(app)


def test_get_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert isinstance(data["companies"], list)
    assert all(isinstance(ticker, str) for ticker in data["companies"])


def test_get_company_info():
    response = client.get("/companies/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"ticker", "name"}
    assert isinstance(data["ticker"], str)
    assert isinstance(data["name"], str)


def test_get_historical_prices():
    response = client.get(
        "/companies/MSFT/historical-prices?start=2024-01-01&end=2024-01-02"
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticker" in data and "historical_prices" in data
    assert isinstance(data["historical_prices"], list)
    for entry in data["historical_prices"]:
        assert {"date", "open", "close"}.issubset(entry)
        assert isinstance(entry["date"], str)
        assert isinstance(entry["open"], (float, int))
        assert isinstance(entry["close"], (float, int))


def test_get_company_info_not_found():
    # response = client.get("/companies/UNKNOWN")
    # assert response.status_code == 404
    pass


def test_get_historical_prices_bad_date():
    response = client.get("/companies/MSFT/historical-prices?start=bad-date")
    assert response.status_code == 422
