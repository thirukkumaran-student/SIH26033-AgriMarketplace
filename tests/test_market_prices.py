"""CEDA market-price integration tests. External HTTP is always mocked."""

from datetime import date
from types import SimpleNamespace

import pytest

from app.modules.market_prices import routes, service
from app.modules.market_prices.service import MarketPriceUpstreamError
from tests.test_auth import auth_headers, obtain_token, register_user


@pytest.fixture(autouse=True)
def clear_market_price_cache():
    service._response_cache.clear()
    yield
    service._response_cache.clear()


def farmer_headers(client):
    assert register_user(client).status_code == 201
    return auth_headers(obtain_token(client))


def test_fetch_market_prices_normalizes_documented_ceda_shape(monkeypatch):
    calls = []

    def fake_json(client, method, path, **kwargs):
        calls.append((method, path, kwargs.get("json")))
        if path == "agmarknet/commodities":
            return {"commodities": [{"id": 78, "name": "Tomato"}]}
        if path == "agmarknet/geographies":
            return {
                "geographies": [
                    {
                        "state_id": 33,
                        "state_name": "Tamil Nadu",
                        "districts": [{"district_id": 603, "district_name": "Chennai"}],
                    }
                ]
            }
        if path == "agmarknet/markets":
            return {"data": [{"market_id": 1001, "market_name": "Koyambedu"}]}
        if path == "agmarknet/prices":
            return {
                "data": [
                    {
                        "date": "2026-09-06",
                        "commodity_id": 78,
                        "census_state_id": 33,
                        "census_district_id": 603,
                        "market_id": 1001,
                        "min_price": 2400,
                        "max_price": 3100,
                        "modal_price": 2800,
                    }
                ]
            }
        raise AssertionError(f"Unexpected CEDA path: {path}")

    monkeypatch.setattr(service, "_json", fake_json)
    result = service.fetch_market_prices(
        api_key="test-key",
        base_url="https://api.ceda.ashoka.edu.in/v1",
        commodity="tomato",
        state="tamil nadu",
        district="chennai",
        from_date=date(2026, 9, 1),
        to_date=date(2026, 9, 7),
    )

    assert result["price_unit"] == "INR_PER_QUINTAL"
    assert result["latest_observation"] == "2026-09-06"
    assert result["markets"][0] == {
        "market": "Koyambedu",
        "market_id": 1001,
        "date": "2026-09-06",
        "min_price": 2400.0,
        "max_price": 3100.0,
        "modal_price": 2800.0,
    }
    assert calls[-1][2]["market_id"] == [1001]
    assert calls[-1][2]["district_id"] == [603]


def test_malformed_ceda_price_response_is_rejected(monkeypatch):
    responses = iter(
        [
            {"commodities": [{"id": 78, "name": "Tomato"}]},
            {
                "geographies": [
                    {
                        "state_id": 33,
                        "state_name": "Tamil Nadu",
                        "districts": [{"district_id": 603, "district_name": "Chennai"}],
                    }
                ]
            },
            {"data": [{"market_id": 1001, "market_name": "Koyambedu"}]},
            {"data": [{"date": "not-a-date", "market_id": 1001}]},
        ]
    )
    monkeypatch.setattr(service, "_json", lambda *args, **kwargs: next(responses))

    with pytest.raises(MarketPriceUpstreamError):
        service.fetch_market_prices(
            api_key="test-key",
            base_url="https://api.ceda.ashoka.edu.in/v1",
            commodity="Tomato",
            state="Tamil Nadu",
            district="Chennai",
            from_date=date(2026, 9, 1),
            to_date=date(2026, 9, 7),
        )


def test_market_price_endpoint_requires_authentication(client):
    response = client.get(
        "/api/market-prices",
        params={"commodity": "Tomato", "state": "Tamil Nadu", "district": "Chennai"},
    )
    assert response.status_code == 401


def test_missing_ceda_key_fails_gracefully(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: SimpleNamespace(ceda_api_key=None, ceda_api_base_url="https://example.invalid/v1"),
    )
    response = client.get(
        "/api/market-prices",
        params={"commodity": "Tomato", "state": "Tamil Nadu", "district": "Chennai"},
        headers=farmer_headers(client),
    )
    assert response.status_code == 503
    assert "CEDA_API_KEY" in response.json()["detail"]


def test_upstream_failure_returns_502_without_crashing(client, monkeypatch):
    monkeypatch.setattr(
        routes,
        "get_settings",
        lambda: SimpleNamespace(ceda_api_key="test-key", ceda_api_base_url="https://example.invalid/v1"),
    )
    monkeypatch.setattr(
        routes,
        "fetch_market_prices",
        lambda **kwargs: (_ for _ in ()).throw(MarketPriceUpstreamError("bad payload")),
    )
    response = client.get(
        "/api/market-prices",
        params={"commodity": "Tomato", "state": "Tamil Nadu", "district": "Chennai"},
        headers=farmer_headers(client),
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "Market prices unavailable from CEDA"

