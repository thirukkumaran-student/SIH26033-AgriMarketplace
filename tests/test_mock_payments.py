"""Tests for the intentionally simple SIH demo-payment flow."""

import re

from app.core.database import SessionLocal
from app.models.order import Order
from tests.test_auth import auth_headers, obtain_token, register_user
from tests.test_orders import register_farmer_with_produce
from tests.test_shipment import register_farmer_with_order


def create_buyer_order(client, *, role="CONSUMER", email="buyer-pay@example.com", total="250"):
    unit_price = float(total) / 10
    farmer_token, produce = register_farmer_with_produce(
        client,
        quantity=100,
        price_per_unit=unit_price,
    )
    assert register_user(client, email=email, role=role).status_code == 201
    buyer_token = obtain_token(client, email=email)
    response = client.post(
        "/api/orders",
        headers=auth_headers(buyer_token),
        json={"produce_id": produce["id"], "quantity": 10},
    )
    assert response.status_code == 201, response.text
    return farmer_token, buyer_token, response.json()


def simulate_payment(client, token, order_id, method):
    return client.post(
        f"/api/orders/{order_id}/simulate-payment",
        headers=auth_headers(token),
        json={"payment_method": method},
    )


def create_logistics_shipment(client, *, assign=False, pickup=False):
    farmer_token, order = register_farmer_with_order(client)
    assert register_user(client, email="logistics-pay@example.com", role="LOGISTICS").status_code == 201
    logistics_token = obtain_token(client, email="logistics-pay@example.com")
    response = client.post(
        "/api/logistics/shipments",
        headers=auth_headers(logistics_token),
        json={
            "order_id": order["id"],
            "pickup_location": "Farm Gate",
            "destination": "Buyer Warehouse",
            "logistics_cost": "175.00",
        },
    )
    assert response.status_code == 200, response.text
    shipment = response.json()
    if assign:
        response = client.post(
            f"/api/logistics/shipments/{shipment['id']}/assign",
            headers=auth_headers(logistics_token),
        )
        assert response.status_code == 200, response.text
        shipment = response.json()
    if pickup:
        response = client.post(
            f"/api/logistics/shipments/{shipment['id']}/pickup",
            headers=auth_headers(logistics_token),
        )
        assert response.status_code == 200, response.text
        shipment = response.json()
    return farmer_token, logistics_token, shipment


def test_consumer_can_pay_own_order(client):
    _, token, order = create_buyer_order(client)
    response = simulate_payment(client, token, order["id"], "UPI")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["payment_status"] == "PAID"
    assert body["payment_method"] == "UPI"
    assert re.fullmatch(r"AGR-PAY-[0-9A-F]{8}", body["payment_reference"])
    assert body["paid_at"] is not None
    assert body["status"] == "PENDING"


def test_bulk_buyer_can_pay_own_order(client):
    _, token, order = create_buyer_order(
        client,
        role="BULK_BUYER",
        email="bulk-pay@example.com",
    )
    response = simulate_payment(client, token, order["id"], "CARD")
    assert response.status_code == 200, response.text
    assert response.json()["payment_status"] == "PAID"


def test_buyer_cannot_pay_another_buyers_order(client):
    _, _, order = create_buyer_order(client)
    assert register_user(client, email="other-buyer@example.com", role="CONSUMER").status_code == 201
    other_token = obtain_token(client, email="other-buyer@example.com")
    response = simulate_payment(client, other_token, order["id"], "UPI")
    assert response.status_code == 403


def test_payment_uses_stored_order_amount_and_rejects_client_amount(client):
    _, token, order = create_buyer_order(client, total="375")
    response = client.post(
        f"/api/orders/{order['id']}/simulate-payment",
        headers=auth_headers(token),
        json={"payment_method": "UPI", "amount": "1.00"},
    )
    assert response.status_code == 422

    response = simulate_payment(client, token, order["id"], "UPI")
    assert response.status_code == 200, response.text
    assert response.json()["total_amount"] == "375.00"
    db = SessionLocal()
    try:
        assert str(db.get(Order, order["id"]).total_amount) == "375.00"
    finally:
        db.close()


def test_cash_succeeds_below_500(client):
    _, token, order = create_buyer_order(client, total="499")
    response = simulate_payment(client, token, order["id"], "CASH")
    assert response.status_code == 200, response.text
    assert response.json()["payment_method"] == "CASH"


def test_cash_is_rejected_at_exactly_500(client):
    _, token, order = create_buyer_order(client, total="500")
    response = simulate_payment(client, token, order["id"], "CASH")
    assert response.status_code == 400
    assert "strictly below" in response.json()["detail"]


def test_cash_is_rejected_above_500(client):
    _, token, order = create_buyer_order(client, total="750")
    response = simulate_payment(client, token, order["id"], "CASH")
    assert response.status_code == 400


def test_duplicate_produce_payment_is_rejected(client):
    _, token, order = create_buyer_order(client)
    assert simulate_payment(client, token, order["id"], "BANK_TRANSFER").status_code == 200
    response = simulate_payment(client, token, order["id"], "UPI")
    assert response.status_code == 409


def test_payment_is_allowed_after_farmer_confirmation(client):
    farmer_token, token, order = create_buyer_order(client)
    response = client.patch(
        f"/api/orders/{order['id']}/status",
        headers=auth_headers(farmer_token),
        json={"status": "CONFIRMED"},
    )
    assert response.status_code == 200, response.text
    response = simulate_payment(client, token, order["id"], "BANK_TRANSFER")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "CONFIRMED"


def test_logistics_user_can_collect_shipment_fee(client):
    _, token, shipment = create_logistics_shipment(client, assign=True)
    response = client.post(
        f"/api/logistics/shipments/{shipment['id']}/collect-fee",
        headers=auth_headers(token),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["logistics_fee_status"] == "COLLECTED"
    assert body["logistics_cost"] == "175.00"
    assert re.fullmatch(r"AGR-LOG-[0-9A-F]{8}", body["logistics_fee_reference"])
    assert body["logistics_fee_collected_at"] is not None
    assert body["status"] == "ASSIGNED"


def test_farmer_consumer_and_admin_cannot_collect_logistics_fee(client):
    farmer_token, _, shipment = create_logistics_shipment(client, assign=True)
    tokens = [
        farmer_token,
        obtain_token(client, email="consumer@example.com"),
        obtain_token(client, email="admin@example.com"),
    ]
    for token in tokens:
        response = client.post(
            f"/api/logistics/shipments/{shipment['id']}/collect-fee",
            headers=auth_headers(token),
        )
        assert response.status_code == 403


def test_duplicate_logistics_fee_collection_is_rejected(client):
    _, token, shipment = create_logistics_shipment(client, assign=True)
    url = f"/api/logistics/shipments/{shipment['id']}/collect-fee"
    assert client.post(url, headers=auth_headers(token)).status_code == 200
    response = client.post(url, headers=auth_headers(token))
    assert response.status_code == 409


def test_logistics_fee_collection_is_rejected_before_assignment(client):
    _, token, shipment = create_logistics_shipment(client)
    response = client.post(
        f"/api/logistics/shipments/{shipment['id']}/collect-fee",
        headers=auth_headers(token),
    )
    assert response.status_code == 400


def test_logistics_fee_can_be_collected_after_pickup(client):
    _, token, shipment = create_logistics_shipment(client, assign=True, pickup=True)
    response = client.post(
        f"/api/logistics/shipments/{shipment['id']}/collect-fee",
        headers=auth_headers(token),
    )
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "PICKED_UP"
