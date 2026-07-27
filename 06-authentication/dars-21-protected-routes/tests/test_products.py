def test_create_category(client):
    response = client.post("/categories/", json={
        "name": "Elektronika",
        "description": "Elektron qurilmalar",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Elektronika"
    assert "id" in data


def test_create_product(client):
    # Avval kategoriya kerak
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    response = client.post("/products/", json={
        "name": "Simli sichqoncha",
        "price": 45000,
        "quantity": 15,
        "category_id": category_id,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Simli sichqoncha"
    assert data["price"] == 45000


def test_read_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Mahsulot topilmadi"


def test_update_product(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    create_response = client.post("/products/", json={
        "name": "Klaviatura", "price": 100000, "category_id": category_id,
    })
    product_id = create_response.json()["id"]

    update_response = client.patch(f"/products/{product_id}", json={"price": 90000})
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 90000
    assert update_response.json()["name"] == "Klaviatura"   # o'zgarmagan


def test_delete_product(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    create_response = client.post("/products/", json={
        "name": "Monitor", "price": 950000, "category_id": category_id,
    })
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404

def test_products_filtering(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    client.post("/products/", json={"name": "Arzon mahsulot", "price": 10000, "category_id": category_id})
    client.post("/products/", json={"name": "Qimmat mahsulot", "price": 500000, "category_id": category_id})

    response = client.get("/products/?min_price=100000")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Qimmat mahsulot"


def test_products_pagination(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    for i in range(5):
        client.post("/products/", json={"name": f"Mahsulot {i}", "price": 10000, "category_id": category_id})

    response = client.get("/products/?limit=2")
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2