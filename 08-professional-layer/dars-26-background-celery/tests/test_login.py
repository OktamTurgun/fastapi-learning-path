def test_login_success(client):
    client.post("/users/register", json={
        "email": "logintest@example.com",
        "password": "ToGriParol123",
        "full_name": "Login Test",
    })

    response = client.post("/users/login", json={
        "email": "logintest@example.com",
        "password": "ToGriParol123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/users/register", json={
        "email": "wrongpass@example.com",
        "password": "ToGriParol123",
        "full_name": "Wrong Pass Test",
    })

    response = client.post("/users/login", json={
        "email": "wrongpass@example.com",
        "password": "NotoGriParol",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


def test_login_nonexistent_email(client):
    response = client.post("/users/login", json={
        "email": "mavjudemas@example.com",
        "password": "har-qanday-parol",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Email yoki parol noto'g'ri"


def test_login_error_messages_are_identical(client):
    """User enumeration himoyasi: ikkala xato holati bir xil xabar qaytarishi kerak"""
    client.post("/users/register", json={
        "email": "enum@example.com",
        "password": "ToGriParol123",
        "full_name": "Enum Test",
    })

    wrong_password_response = client.post("/users/login", json={
        "email": "enum@example.com",
        "password": "NotoGriParol",
    })
    nonexistent_email_response = client.post("/users/login", json={
        "email": "mavjudemas2@example.com",
        "password": "har-qanday-parol",
    })

    assert wrong_password_response.status_code == nonexistent_email_response.status_code
    assert wrong_password_response.json()["detail"] == nonexistent_email_response.json()["detail"]