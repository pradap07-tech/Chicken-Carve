from __future__ import annotations

from pathlib import Path

import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path: Path):
    db_file = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE": str(db_file)})

    with app.test_client() as test_client:
        yield test_client


def test_products_seeded_and_filterable(client):
    response = client.get("/api/products")
    assert response.status_code == 200
    payload = response.get_json()
    assert len(payload["products"]) >= 120

    filtered = client.get("/api/products?category=Burgers&sort=price_desc")
    data = filtered.get_json()["products"]
    assert len(data) == 5
    assert data[0]["price"] >= data[-1]["price"]


def test_cart_checkout_and_orders(client):
    products = client.get("/api/products").get_json()["products"]
    item_id = products[0]["id"]

    add_response = client.post("/api/cart/add", json={"product_id": item_id, "quantity": 2})
    assert add_response.status_code == 201
    cart = add_response.get_json()
    assert cart["count"] == 2

    update_response = client.patch(f"/api/cart/{item_id}", json={"quantity": 1})
    assert update_response.status_code == 200
    assert update_response.get_json()["count"] == 1

    checkout = client.post(
        "/api/checkout",
        json={
            "customer_name": "Alex User",
            "address": "42 Main Street",
            "phone": "123-555-0199",
            "notes": "Leave at door",
        },
    )
    assert checkout.status_code == 201
    order = checkout.get_json()
    assert order["total"] >= order["subtotal"]

    orders_response = client.get("/api/orders")
    orders = orders_response.get_json()["orders"]
    assert len(orders) == 1
    assert orders[0]["customer_name"] == "Alex User"
    assert len(orders[0]["items"]) == 1


def test_checkout_validation(client):
    response = client.post("/api/checkout", json={"customer_name": "Only Name"})
    assert response.status_code == 400
    assert "required" in response.get_json()["error"].lower()
