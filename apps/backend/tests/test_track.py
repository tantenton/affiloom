"""Tests for the anonymous analytics tracking endpoints (M4-001)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client(initialized_db: str):
    with TestClient(app) as c:
        yield c


def test_track_pageview_returns_204(client: TestClient) -> None:
    response = client.post(
        "/api/track/pageview",
        json={"path": "/produk/demo-1"},
        headers={"User-Agent": "test-agent/1.0"},
    )
    assert response.status_code == 204


def test_track_click_returns_204(client: TestClient) -> None:
    response = client.post(
        "/api/track/click",
        json={
            "product_id": "demo-1",
            "article_id": None,
            "url": "https://example.com/p",
        },
    )
    assert response.status_code == 204


def test_track_pageview_validates_path(client: TestClient) -> None:
    response = client.post("/api/track/pageview", json={"path": ""})
    assert response.status_code == 422
