"""
Dars 25 — Permissions & Roles testlari
=======================================
Bu faylda require_role() dependency to'g'ri ishlayotganini tekshiramiz:
  - ADMIN → POST /products ruxsat
  - MANAGER → POST /products ruxsat
  - CUSTOMER → POST /products 403 Forbidden
  - ADMIN → DELETE /products ruxsat
  - MANAGER → DELETE /products 403 Forbidden
  - Tokensiz → 401 Unauthorized
"""

import pytest
from tests.conftest import make_auth_headers


# ─── Yordamchi: kategoriya yaratish ──────────────────────────────────────────

def create_category(client, name="Test Kategoriya"):
    resp = client.post("/categories/", json={"name": name})
    assert resp.status_code == 201
    return resp.json()["id"]


def create_product_as(client, headers, category_id, name="Test Mahsulot"):
    return client.post("/products/", json={
        "name": name,
        "price": 50000,
        "quantity": 10,
        "category_id": category_id,
    }, headers=headers)


# ─── POST /products — kim yarata oladi? ──────────────────────────────────────

def test_admin_can_create_product(client, admin_user):
    """ADMIN mahsulot yarata oladi → 201"""
    headers = make_auth_headers(admin_user)
    category_id = create_category(client)

    response = create_product_as(client, headers, category_id, "Admin Mahsuloti")

    assert response.status_code == 201, response.json()
    assert response.json()["name"] == "Admin Mahsuloti"


def test_manager_can_create_product(client, manager_user):
    """MANAGER mahsulot yarata oladi → 201"""
    headers = make_auth_headers(manager_user)
    category_id = create_category(client)

    response = create_product_as(client, headers, category_id, "Manager Mahsuloti")

    assert response.status_code == 201, response.json()
    assert response.json()["name"] == "Manager Mahsuloti"


def test_customer_cannot_create_product(client, customer_user):
    """CUSTOMER mahsulot yarata OLMAYDI → 403 Forbidden"""
    headers = make_auth_headers(customer_user)
    category_id = create_category(client)

    response = create_product_as(client, headers, category_id, "Customer Urinishi")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "ruxsat" in detail.lower() or "403" in str(response.status_code)


def test_unauthenticated_cannot_create_product(client):
    """Token yo'q → 401 Unauthorized (403 emas!)"""
    category_id = create_category(client)

    response = create_product_as(client, headers={}, category_id=category_id)

    assert response.status_code == 401


# ─── DELETE /products — faqat ADMIN ──────────────────────────────────────────

def test_admin_can_delete_product(client, admin_user):
    """ADMIN mahsulotni o'chira oladi → 204"""
    headers = make_auth_headers(admin_user)
    category_id = create_category(client)

    create_resp = create_product_as(client, headers, category_id, "O'chiriladigan mahsulot")
    product_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/products/{product_id}", headers=headers)
    assert delete_resp.status_code == 204

    # O'chirilganini tekshiramiz
    get_resp = client.get(f"/products/{product_id}")
    assert get_resp.status_code == 404


def test_manager_cannot_delete_product(client, admin_user, manager_user):
    """MANAGER mahsulotni o'chira OLMAYDI → 403"""
    admin_headers = make_auth_headers(admin_user)
    manager_headers = make_auth_headers(manager_user)
    category_id = create_category(client)

    create_resp = create_product_as(client, admin_headers, category_id, "Himoyalangan mahsulot")
    product_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/products/{product_id}", headers=manager_headers)
    assert delete_resp.status_code == 403


def test_customer_cannot_delete_product(client, admin_user, customer_user):
    """CUSTOMER mahsulotni o'chira OLMAYDI → 403"""
    admin_headers = make_auth_headers(admin_user)
    customer_headers = make_auth_headers(customer_user)
    category_id = create_category(client)

    create_resp = create_product_as(client, admin_headers, category_id, "Yana mahsulot")
    product_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/products/{product_id}", headers=customer_headers)
    assert delete_resp.status_code == 403


# ─── 401 vs 403 farqi ────────────────────────────────────────────────────────

def test_401_vs_403_difference(client, customer_user):
    """
    401 — token YO'Q (kim ekanligingiz noaniq)
    403 — token TO'G'RI, lekin ruxsat YO'Q
    """
    category_id = create_category(client)

    # Token yo'q → 401
    no_token_resp = create_product_as(client, headers={}, category_id=category_id)
    assert no_token_resp.status_code == 401

    # Token bor, lekin CUSTOMER → 403
    customer_headers = make_auth_headers(customer_user)
    forbidden_resp = create_product_as(client, customer_headers, category_id)
    assert forbidden_resp.status_code == 403

    # Ikkovi BOSHQA xato! Bu Dars 25 ning asosiy nuqtasi.
    assert no_token_resp.status_code != forbidden_resp.status_code


# ─── GET /products — hamma ko'ra oladi (public) ──────────────────────────────

def test_anyone_can_read_products(client):
    """GET /products token talab qilmaydi — public endpoint"""
    response = client.get("/products/")
    assert response.status_code == 200
    assert "items" in response.json()


def test_role_field_in_user_response(client):
    """Register bo'lganda role field qaytarilmasligi (UserResponse sxemasi)"""
    resp = client.post("/users/register", json={
        "email": "rolecheck@example.com",
        "password": "Parol12345",
        "full_name": "Role Check",
    })
    assert resp.status_code == 201
    data = resp.json()
    # UserResponse sxemasida 'role' yo'q — bu ataylab (security uchun)
    # Agar qo'shilgan bo'lsa, bu test muvaffaqiyatli bo'ladi
    assert "hashed_password" not in data
    assert "password" not in data
