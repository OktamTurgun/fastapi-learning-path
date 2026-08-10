import pytest


@pytest.mark.asyncio
async def test_health_check_endpoint(client):
    """Health check endpoint 200 OK va to'g'ri status qaytarishini tekshirish"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "environment" in data
    assert "version" in data
