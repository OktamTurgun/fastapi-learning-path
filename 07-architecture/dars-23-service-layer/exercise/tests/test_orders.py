def test_create_order(client):
    customer_response = client.post(
        "/customers/",
        json={"full_name": "Elektronika", "phone": "998991112233"},
    )
    customer_id = customer_response.json()["id"]

    response = client.post(
        "/orders/",
        json={
            "total_amount": 150.5,
            "status": "pending",
            "delivery_address": "Toshkent",
            "customer_id": customer_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == 150.5
    assert data["status"] == "pending"
    assert data["customer"]["id"] == customer_id
    assert "id" in data


def test_read_order_not_found(client):
    response = client.get("/orders/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Buyurtma topilmadi"


def test_update_order(client):
    customer_response = client.post(
        "/customers/",
        json={"full_name": "Elektronika", "phone": "998995556677"},
    )
    customer_id = customer_response.json()["id"]

    create_response = client.post(
        "/orders/",
        json={
            "total_amount": 100.0,
            "status": "pending",
            "delivery_address": "Samarqand",
            "customer_id": customer_id,
        },
    )
    order_id = create_response.json()["id"]

    update_response = client.patch(
        f"/orders/{order_id}",
        json={"status": "shipped", "delivery_address": "Andijon"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "shipped"
    assert update_response.json()["delivery_address"] == "Andijon"


def test_delete_order(client):
    customer_response = client.post(
        "/customers/",
        json={"full_name": "Elektronika", "phone": "998998887766"},
    )
    customer_id = customer_response.json()["id"]

    create_response = client.post(
        "/orders/",
        json={
            "total_amount": 250.0,
            "status": "pending",
            "delivery_address": "Buxoro",
            "customer_id": customer_id,
        },
    )
    order_id = create_response.json()["id"]

    delete_response = client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 404


def test_orders_filtering(client):
    customer_response = client.post(
        "/customers/",
        json={"full_name": "John Doe", "phone": "998991122334"},
    )
    customer_id = customer_response.json()["id"]

    client.post(
        "/orders/",
        json={
            "total_amount": 100.0,
            "status": "pending",
            "delivery_address": "Toshkent",
            "customer_id": customer_id,
        },
    )
    client.post(
        "/orders/",
        json={
            "total_amount": 500.0,
            "status": "pending",
            "delivery_address": "Buxoro",
            "customer_id": customer_id,
        },
    )

    response = client.get("/orders/?min_total_amount=200")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["total_amount"] == 500.0


def test_orders_pagination(client):
    customer_response = client.post(
        "/customers/",
        json={"full_name": "John Doe", "phone": "998991122335"},
    )
    customer_id = customer_response.json()["id"]

    for i in range(5):
        client.post(
            "/orders/",
            json={
                "total_amount": float(10000 + i),
                "status": "pending",
                "delivery_address": f"Manzil {i}",
                "customer_id": customer_id,
            },
        )

    response = client.get("/orders/?limit=2")
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2