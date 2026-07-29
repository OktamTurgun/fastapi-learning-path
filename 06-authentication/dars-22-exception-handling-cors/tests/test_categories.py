def test_create_category(client):
    response = client.post("/categories/", json={
        "name": "Elektronika",
        "description": "Elektron qurilmalar",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Elektronika"
    assert "id" in data


def test_read_category_not_found(client):
    response = client.get("/categories/999")
    assert response.status_code == 404