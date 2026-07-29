import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
