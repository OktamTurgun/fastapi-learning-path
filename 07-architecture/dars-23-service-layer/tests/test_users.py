from app.core.security import verify_password, hash_password


def test_register_user(client):
    response = client.post("/users/register", json={
        "email": "testuser@example.com",
        "password": "MenSirliParolim123",
        "full_name": "Test Foydalanuvchi",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["full_name"] == "Test Foydalanuvchi"
    assert data["is_active"] is True
    assert "id" in data


def test_register_response_has_no_password_fields(client):
    response = client.post("/users/register", json={
        "email": "secure@example.com",
        "password": "MaxfiyParol456",
        "full_name": "Xavfsiz Foydalanuvchi",
    })
    assert response.status_code == 201
    data = response.json()
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post("/users/register", json={
        "email": "duplicate@example.com",
        "password": "Parol123",
        "full_name": "Birinchi Foydalanuvchi",
    })

    response = client.post("/users/register", json={
        "email": "duplicate@example.com",
        "password": "BoshqaParol456",
        "full_name": "Ikkinchi Foydalanuvchi",
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Bu email allaqachon ro'yxatdan o'tgan"


def test_verify_password_correct():
    hashed = hash_password("MyRealPassword")
    assert verify_password("MyRealPassword", hashed) is True


def test_verify_password_incorrect():
    hashed = hash_password("MyRealPassword")
    assert verify_password("WrongPassword", hashed) is False