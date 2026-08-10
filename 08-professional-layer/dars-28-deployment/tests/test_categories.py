import pytest


@pytest.mark.asyncio
async def test_create_category_admin(client, admin_headers):
    response = await client.post(
        "/categories",
        json={"name": "Elektronika", "description": "Maishiy texnika"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Elektronika"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_get_categories(client, admin_headers):
    await client.post(
        "/categories",
        json={"name": "Kitoblar", "description": "Badiiy adabiyot"},
        headers=admin_headers,
    )
    response = await client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
