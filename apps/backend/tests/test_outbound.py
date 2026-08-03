"""Tests for centralized affiliate outbound redirect service (M5)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_outbound_redirect_success(client: TestClient) -> None:
    response = client.get(
        "/api/outbound/go?to=https://example.com/product&product_id=demo-1&merchant=Tokopedia",
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/product"


def test_outbound_redirect_invalid_url(client: TestClient) -> None:
    response = client.get("/api/outbound/go?to=javascript:alert(1)")
    assert response.status_code == 400
