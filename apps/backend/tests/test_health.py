"""Tests for health, readiness, dependency probes, and metrics."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def client(initialized_db: str):
    with TestClient(app) as c:
        yield c


def test_health_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_with_db(client: TestClient) -> None:
    r = client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    deps = {d["name"]: d for d in body["deps"]}
    assert deps["database"]["healthy"] is True
    assert deps["database"]["required"] is True
    # redis and search are optional / disabled in tests
    assert deps["redis"]["required"] is False
    assert deps["search"]["required"] is False


def test_deps_detail(client: TestClient) -> None:
    r = client.get("/deps")
    assert r.status_code == 200
    body = r.json()
    assert "status" in body
    assert isinstance(body["deps"], list)
    names = {d["name"] for d in body["deps"]}
    assert "database" in names
    assert "redis" in names
    assert "search" in names


def test_metrics(client: TestClient) -> None:
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["app"] == "affiloom"
    assert "products" in body
    assert "sync" in body
    assert "content" in body
    assert isinstance(body["products"]["total"], int)
    assert isinstance(body["sync"]["healthy"], bool)
