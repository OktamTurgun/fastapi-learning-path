def get_token(client, email="protected@example.com", password="ProtectedParol123"):
    """Yordamchi funksiya — ro'yxatdan o'tkazib, login qilib, token qaytaradi"""
    client.post("/users/register", json={
        "email": email,
        "password": password,
        "full_name": "Protected Test User",
    })
    login_response = client.post("/users/login", json={
        "email": email,
        "password": password,
    })
    return login_response.json()["access_token"]


def test_read_me_with_valid_token(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "protected@example.com"
    assert data["full_name"] == "Protected Test User"


def test_read_me_without_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_read_me_with_invalid_token(client):
    headers = {"Authorization": "Bearer bu-yolgon-soxta-token"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401


def test_create_product_with_valid_token(client):
    token = get_token(client, email="productcreator@example.com", password="ParolCreator123")
    headers = {"Authorization": f"Bearer {token}"}

    category_response = client.post("/categories/", json={"name": "Test Kategoriya"})
    category_id = category_response.json()["id"]

    response = client.post("/products/", json={
        "name": "Himoyalangan mahsulot",
        "price": 75000,
        "category_id": category_id,
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Himoyalangan mahsulot"


def test_create_product_without_token(client):
    category_response = client.post("/categories/", json={"name": "Test Kategoriya 2"})
    category_id = category_response.json()["id"]

    response = client.post("/products/", json={
        "name": "Tokensiz urinish",
        "price": 10000,
        "category_id": category_id,
    })
    assert response.status_code == 401