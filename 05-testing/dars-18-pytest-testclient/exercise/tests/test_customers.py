def test_create_customer(client):
    response = client.post("/customers/", json={
        "full_name": "John Doe",
        "phone": "998991234567"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "John Doe"
    assert data["phone"] == "998991234567"
    assert "id" in data


def test_read_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Mijoz topilmadi"