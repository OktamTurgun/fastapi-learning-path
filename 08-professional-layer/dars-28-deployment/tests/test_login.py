import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    # 1. Ro'yxatdan o'tish
    reg_res = await client.post(
        "/users/register",
        json={"email": "user@test.com", "password": "userpass123", "full_name": "Test User"}
    )
    assert reg_res.status_code == 201

    # 2. Login qilish
    login_res = await client.post(
        "/users/login",
        data={"username": "user@test.com", "password": "userpass123"}
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # 3. /users/me endpointini tekshirish
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = await client.get("/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "user@test.com"
