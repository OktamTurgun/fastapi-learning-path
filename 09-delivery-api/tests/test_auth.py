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
