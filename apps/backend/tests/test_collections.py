"""Tests for public collections endpoints (M7)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_collections_empty(client: TestClient) -> None:
    response = client.get("/api/collections")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_collection_not_found(client: TestClient) -> None:
    response = client.get("/api/collections/nonexistent-slug")
    assert response.status_code == 404
