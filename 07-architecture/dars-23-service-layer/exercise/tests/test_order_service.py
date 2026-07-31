import pytest
from fastapi.testclient import TestClient


def test_create_order_with_valid_customer(client: TestClient):
    """Mavjud mijoz bilan buyurtma yaratish -> 201 Created"""
    # 1. Mijoz yaratamiz (full_name required)
    cust_resp = client.post("/customers/", json={"full_name": "Ali Valiyev", "phone": "+998901234567"})
    assert cust_resp.status_code == 201
    customer_id = cust_resp.json()["id"]

    # 2. Shu mijozga buyurtma yaratamiz
    order_resp = client.post(
        "/orders/",
        json={
            "total_amount": 150.0,
            "status": "pending",
            "delivery_address": "Tashkent, Chilonzor",
            "customer_id": customer_id,
        },
    )
    assert order_resp.status_code == 201
    data = order_resp.json()
    assert data["customer"]["id"] == customer_id
    assert data["total_amount"] == 150.0


def test_create_order_with_invalid_customer(client: TestClient):
    """Mavjud bo'lmagan mijoz bilan buyurtma yaratish -> 400 Bad Request"""
    order_resp = client.post(
        "/orders/",
        json={
            "total_amount": 200.0,
            "status": "pending",
            "delivery_address": "Samarkand",
            "customer_id": 9999,  # Mavjud emas
        },
    )
    assert order_resp.status_code == 400
    assert "Customer with id 9999 does not exist" in order_resp.json()["detail"]


def test_update_order_with_invalid_customer(client: TestClient):
    """Mavjud bo'lmagan customer_id bilan buyurtmani yangilash -> 400 Bad Request"""
    # 1. Mijoz va buyurtma yaratamiz
    cust_resp = client.post("/customers/", json={"full_name": "Vali Aliyev"})
    assert cust_resp.status_code == 201
    customer_id = cust_resp.json()["id"]

    order_resp = client.post(
        "/orders/",
        json={"total_amount": 100.0, "customer_id": customer_id},
    )
    assert order_resp.status_code == 201
    order_id = order_resp.json()["id"]

    # 2. Mavjud bo'lmagan customer_id bilan yangilaymiz
    update_resp = client.patch(f"/orders/{order_id}", json={"customer_id": 8888})
    assert update_resp.status_code == 400
    assert "Customer with id 8888 does not exist" in update_resp.json()["detail"]


def test_delete_order_not_found(client: TestClient):
    """Mavjud bo'lmagan buyurtmani o'chirish -> 404 Not Found"""
    delete_resp = client.delete("/orders/9999")
    assert delete_resp.status_code == 404
    assert delete_resp.json()["detail"] == "Buyurtma topilmadi"


def test_update_order_not_found(client: TestClient):
    """Mavjud bo'lmagan buyurtmani yangilash -> 404 Not Found"""
    update_resp = client.patch("/orders/9999", json={"total_amount": 500.0})
    assert update_resp.status_code == 404
    assert update_resp.json()["detail"] == "Buyurtma topilmadi"
