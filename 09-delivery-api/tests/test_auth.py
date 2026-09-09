import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "Yangi Foydalanuvchi",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "Yangi Foydalanuvchi"
    assert "id" in data
    assert "hashed_password" not in data
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "customer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "Birinchi User",
    }
    first_resp = await client.post("/auth/register", json=payload)
    assert first_resp.status_code == 201

    second_resp = await client.post("/auth/register", json=payload)
    assert second_resp.status_code == 400
    assert second_resp.json()["detail"] == "Email allaqachon ro'yxatdan o'tgan"


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "not-a-valid-email",
            "password": "password123",
            "full_name": "Test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_missing_password(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "valid@example.com",
            "full_name": "Test",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    # Avval ro'yxatdan o'tamiz
    await client.post(
        "/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword",
            "full_name": "Login User",
        },
    )

    # Login qilamiz
    response = await client.post(
        "/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "mypassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpassword",
            "full_name": "User",
        },
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


@pytest.mark.asyncio
async def test_login_nonexistent_email(client):
    response = await client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "any_password",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


# ==========================================
# ROLLARNI TANLASH VA BIRIKTIRISH TESTLARI
# ==========================================

@pytest.mark.asyncio
async def test_register_courier_success(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "courier_new@example.com",
            "password": "password123",
            "full_name": "Yangi Kuryer",
            "role": "courier",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "courier_new@example.com"
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "courier"


@pytest.mark.asyncio
async def test_register_admin_with_valid_secret(client):
    from app.core.config import settings

    response = await client.post(
        "/auth/register",
        json={
            "email": "admin_new@example.com",
            "password": "password123",
            "full_name": "Yangi Admin",
            "role": "admin",
            "admin_secret": settings.admin_secret_key,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin_new@example.com"
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "admin"


@pytest.mark.asyncio
async def test_register_admin_with_invalid_secret(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "admin_fail@example.com",
            "password": "password123",
            "full_name": "Soxta Admin",
            "role": "admin",
            "admin_secret": "not_the_real_secret",
        },
    )
    assert response.status_code == 400
    assert "admin_secret" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_admin_without_secret(client):
    response = await client.post(
        "/auth/register",
        json={
            "email": "admin_no_secret@example.com",
            "password": "password123",
            "full_name": "No Secret Admin",
            "role": "admin",
        },
    )
    assert response.status_code == 400
    assert "admin_secret" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_can_assign_role(client, admin_headers, customer_user):
    # Admin customer_user ga 'courier' rolini ham biriktiradi
    response = await client.post(
        "/auth/assign-role",
        headers=admin_headers,
        json={
            "user_id": str(customer_user.id),
            "role": "courier",
        },
    )
    assert response.status_code == 200
    data = response.json()
    role_names = [r["name"] for r in data["roles"]]
    assert "customer" in role_names
    assert "courier" in role_names


@pytest.mark.asyncio
async def test_non_admin_cannot_assign_role(client, customer_headers, customer_user):
    # Oddiy mijoz boshqa birovga rol bera olmaydi (403 Forbidden)
    response = await client.post(
        "/auth/assign-role",
        headers=customer_headers,
        json={
            "user_id": str(customer_user.id),
            "role": "admin",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_cannot_assign_role(client, customer_user):
    response = await client.post(
        "/auth/assign-role",
        json={
            "user_id": str(customer_user.id),
            "role": "courier",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_assign_role_nonexistent_user(client, admin_headers):
    import uuid
    random_id = str(uuid.uuid4())
    response = await client.post(
        "/auth/assign-role",
        headers=admin_headers,
        json={
            "user_id": random_id,
            "role": "courier",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Foydalanuvchi topilmadi"
