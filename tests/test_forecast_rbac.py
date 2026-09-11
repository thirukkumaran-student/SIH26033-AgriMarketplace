"""Regression tests for forecast/suggestion authorization."""

from tests.test_auth import auth_headers, obtain_token, register_user


def headers_for(client, role: str, email: str):
    assert register_user(client, role=role, email=email).status_code == 201
    return auth_headers(obtain_token(client, email=email))


def test_forecast_history_requires_authentication(client):
    assert client.get("/api/forecast/").status_code == 401


def test_consumer_cannot_access_forecasts(client):
    headers = headers_for(client, "CONSUMER", "consumer@example.com")
    assert client.get("/api/forecast/", headers=headers).status_code == 403


def test_farmer_can_read_forecast_history(client):
    headers = headers_for(client, "FARMER", "farmer-rbac@example.com")
    response = client.get("/api/forecast/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_only_admin_can_train_forecast_model(client):
    headers = headers_for(client, "FARMER", "farmer-train@example.com")
    assert client.post("/api/forecast/train", headers=headers).status_code == 403


def test_consumer_cannot_generate_suggestions(client):
    headers = headers_for(client, "CONSUMER", "consumer-suggestion@example.com")
    response = client.post(
        "/api/suggestions/",
        headers=headers,
        json={
            "crop": "Tomato",
            "district_name": "Chennai",
            "date": "2026-09-07",
            "lag_1": 10,
            "lag_2": 12,
            "days_since_previous": 1,
            "available_quantity": 20,
        },
    )
    assert response.status_code == 403
