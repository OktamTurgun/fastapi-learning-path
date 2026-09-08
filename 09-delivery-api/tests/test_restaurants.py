import uuid
import pytest


@pytest.mark.asyncio
async def test_admin_create_restaurant(client, admin_headers):
    response = await client.post(
        "/restaurants/",
        headers=admin_headers,
        json={
            "name": "Osh Markazi",
            "address": "Navoiy ko'chasi, 15",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Osh Markazi"
    assert data["address"] == "Navoiy ko'chasi, 15"
    assert data["is_active"] is True
    assert "id" in data
    assert data["menu_items"] == []


@pytest.mark.asyncio
async def test_customer_cannot_create_restaurant(client, customer_headers):
    response = await client.post(
        "/restaurants/",
        headers=customer_headers,
        json={
            "name": "Ruxsatsiz Restoran",
            "address": "Toshkent",
            "is_active": True,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Bu amalni bajarish uchun ruxsatingiz yo'q"


@pytest.mark.asyncio
async def test_unauthenticated_cannot_create_restaurant(client):
    response = await client.post(
        "/restaurants/",
        json={
            "name": "Tokensiz Restoran",
            "address": "Toshkent",
            "is_active": True,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_add_menu_item(client, admin_headers, sample_restaurant):
    response = await client.post(
        f"/restaurants/{sample_restaurant.id}/menu-items",
        headers=admin_headers,
        json={
            "name": "Somsa",
            "price": 12000.0,
            "is_available": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Somsa"
    assert data["price"] == 12000.0
    assert data["restaurant_id"] == str(sample_restaurant.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_customer_cannot_add_menu_item(client, customer_headers, sample_restaurant):
    response = await client.post(
        f"/restaurants/{sample_restaurant.id}/menu-items",
        headers=customer_headers,
        json={
            "name": "Somsa",
            "price": 12000.0,
            "is_available": True,
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_menu_item_nonexistent_restaurant(client, admin_headers):
    fake_id = uuid.uuid4()
    response = await client.post(
        f"/restaurants/{fake_id}/menu-items",
        headers=admin_headers,
        json={
            "name": "Shashlik",
            "price": 18000.0,
            "is_available": True,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Restoran topilmadi"


@pytest.mark.asyncio
async def test_get_restaurant_by_id(client, customer_headers, sample_restaurant, sample_menu_item):
    response = await client.get(
        f"/restaurants/{sample_restaurant.id}",
        headers=customer_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_restaurant.id)
    assert data["name"] == sample_restaurant.name
    assert len(data["menu_items"]) == 1
    assert data["menu_items"][0]["id"] == str(sample_menu_item.id)
    assert data["menu_items"][0]["name"] == sample_menu_item.name


@pytest.mark.asyncio
async def test_get_nonexistent_restaurant(client, customer_headers):
    fake_id = uuid.uuid4()
    response = await client.get(
        f"/restaurants/{fake_id}",
        headers=customer_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Restoran topilmadi"


@pytest.mark.asyncio
async def test_get_restaurant_unauthenticated(client, sample_restaurant):
    response = await client.get(f"/restaurants/{sample_restaurant.id}")
    assert response.status_code == 401
