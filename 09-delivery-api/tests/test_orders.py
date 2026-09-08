import uuid
import pytest


@pytest.mark.asyncio
async def test_create_parcel_order_success(client, customer_user, customer_headers):
    response = await client.post(
        "/orders/parcel",
        headers=customer_headers,
        json={
            "order_type": "parcel",
            "weight_kg": 3.5,
            "pickup_address": "Amir Temur ko'chasi, 1",
            "dropoff_address": "Buyuk Ipak Yo'li, 10",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "parcel"
    assert data["customer_id"] == str(customer_user.id)
    assert data["status"] == "pending"
    assert data["weight_kg"] == 3.5
    # total_price = 5000 + (3.5 * 2000) = 12000.0
    assert data["total_price"] == 12000.0
    assert "id" in data


@pytest.mark.asyncio
async def test_create_parcel_order_unauthenticated(client):
    response = await client.post(
        "/orders/parcel",
        json={
            "order_type": "parcel",
            "weight_kg": 2.0,
            "pickup_address": "A",
            "dropoff_address": "B",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_food_order_success(
    client, customer_user, customer_headers, sample_restaurant, sample_menu_item
):
    response = await client.post(
        "/orders/food",
        headers=customer_headers,
        json={
            "order_type": "food",
            "restaurant_id": str(sample_restaurant.id),
            "delivery_address": "Chilonzor 1-mavze, 5-uy",
            "items": [
                {
                    "menu_item_id": str(sample_menu_item.id),
                    "quantity": 2,
                }
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "food"
    assert data["customer_id"] == str(customer_user.id)
    assert data["restaurant_id"] == str(sample_restaurant.id)
    assert data["status"] == "pending"
    # sample_menu_item narxi 45000 * 2 = 90000.0
    assert data["total_price"] == 90000.0


@pytest.mark.asyncio
async def test_create_food_order_invalid_menu_item(
    client, customer_headers, sample_restaurant
):
    fake_item_id = uuid.uuid4()
    response = await client.post(
        "/orders/food",
        headers=customer_headers,
        json={
            "order_type": "food",
            "restaurant_id": str(sample_restaurant.id),
            "delivery_address": "Chilonzor 1-mavze, 5-uy",
            "items": [
                {
                    "menu_item_id": str(fake_item_id),
                    "quantity": 1,
                }
            ],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Ba'zi menu_item_id lar noto'g'ri yoki mavjud emas"


@pytest.mark.asyncio
async def test_courier_can_update_parcel_status(client, customer_headers, courier_headers):
    # 1. Customer buyurtma yaratadi
    create_resp = await client.post(
        "/orders/parcel",
        headers=customer_headers,
        json={
            "order_type": "parcel",
            "weight_kg": 1.0,
            "pickup_address": "Manzil A",
            "dropoff_address": "Manzil B",
        },
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    # 2. Courier maqomni in_transit ga o'zgartiradi
    update_resp = await client.patch(
        f"/orders/parcel/{order_id}/status",
        headers=courier_headers,
        json={"status": "in_transit"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "in_transit"

    # 3. Courier maqomni delivered ga o'zgartiradi
    delivered_resp = await client.patch(
        f"/orders/parcel/{order_id}/status",
        headers=courier_headers,
        json={"status": "delivered"},
    )
    assert delivered_resp.status_code == 200
    assert delivered_resp.json()["status"] == "delivered"


@pytest.mark.asyncio
async def test_customer_cannot_update_parcel_status(client, customer_headers):
    create_resp = await client.post(
        "/orders/parcel",
        headers=customer_headers,
        json={
            "order_type": "parcel",
            "weight_kg": 1.0,
            "pickup_address": "Manzil A",
            "dropoff_address": "Manzil B",
        },
    )
    order_id = create_resp.json()["id"]

    # Customer maqomni o'zgartirishga uringanda 403 olishi kerak
    update_resp = await client.patch(
        f"/orders/parcel/{order_id}/status",
        headers=customer_headers,
        json={"status": "delivered"},
    )
    assert update_resp.status_code == 403
    assert update_resp.json()["detail"] == "Bu amalni bajarish uchun ruxsatingiz yo'q"


@pytest.mark.asyncio
async def test_courier_can_update_food_status(
    client, customer_headers, courier_headers, sample_restaurant, sample_menu_item
):
    create_resp = await client.post(
        "/orders/food",
        headers=customer_headers,
        json={
            "order_type": "food",
            "restaurant_id": str(sample_restaurant.id),
            "delivery_address": "Toshkent",
            "items": [{"menu_item_id": str(sample_menu_item.id), "quantity": 1}],
        },
    )
    assert create_resp.status_code == 201
    order_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/orders/food/{order_id}/status",
        headers=courier_headers,
        json={"status": "delivered"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "delivered"


@pytest.mark.asyncio
async def test_customer_cannot_update_food_status(
    client, customer_headers, sample_restaurant, sample_menu_item
):
    create_resp = await client.post(
        "/orders/food",
        headers=customer_headers,
        json={
            "order_type": "food",
            "restaurant_id": str(sample_restaurant.id),
            "delivery_address": "Toshkent",
            "items": [{"menu_item_id": str(sample_menu_item.id), "quantity": 1}],
        },
    )
    order_id = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/orders/food/{order_id}/status",
        headers=customer_headers,
        json={"status": "delivered"},
    )
    assert update_resp.status_code == 403


@pytest.mark.asyncio
async def test_update_status_nonexistent_order(client, courier_headers):
    fake_id = uuid.uuid4()
    response = await client.patch(
        f"/orders/parcel/{fake_id}/status",
        headers=courier_headers,
        json={"status": "delivered"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Buyurtma topilmadi"
