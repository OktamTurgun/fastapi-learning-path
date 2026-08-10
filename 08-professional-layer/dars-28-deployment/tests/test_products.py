import pytest


@pytest.mark.asyncio
async def test_create_and_get_product(client, admin_headers):
    # 1. Kategoriya yaratish
    cat_res = await client.post(
        "/categories",
        json={"name": "Smartfonlar"},
        headers=admin_headers,
    )
    cat_id = cat_res.json()["id"]

    # 2. Mahsulot yaratish
    prod_res = await client.post(
        "/products",
        json={"title": "iPhone 15", "price": 999.99, "category_id": cat_id},
        headers=admin_headers,
    )
    assert prod_res.status_code == 201
    prod_data = prod_res.json()
    assert prod_data["title"] == "iPhone 15"

    # 3. Olish
    get_res = await client.get(f"/products/{prod_data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["category"]["name"] == "Smartfonlar"
