"""Tests for the admin dashboard summary endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from config import settings
from main import app
from services.search import reset_indexer


@pytest.fixture()
def admin_client(initialized_db: str, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "test-admin-token")
    reset_indexer()
    with TestClient(app) as client:
        yield client


def _auth() -> dict[str, str]:
    return {"Authorization": "Bearer test-admin-token"}


def test_dashboard_requires_token(initialized_db: str, monkeypatch) -> None:
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "")
    with TestClient(app) as c:
        r = c.get("/api/admin/dashboard/summary")
    assert r.status_code == 503


def test_dashboard_empty_db(admin_client: TestClient) -> None:
    r = admin_client.get("/api/admin/dashboard/summary", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["products"]["total"] == 0
    assert body["products"]["active"] == 0
    assert body["products"]["merchants"] == 0
    assert body["sync"]["total_runs"] == 0
    assert body["sync"]["healthy"] is True
    assert body["content"]["articles_total"] == 0


def test_dashboard_after_sync(admin_client: TestClient) -> None:
    # Trigger a sync
    r = admin_client.post("/api/admin/sync/demo", headers=_auth())
    assert r.status_code == 200

    r = admin_client.get("/api/admin/dashboard/summary", headers=_auth())
    body = r.json()
    assert body["products"]["total"] == 10
    assert body["products"]["active"] == 10
    assert body["products"]["merchants"] == 1
    assert body["sync"]["total_runs"] == 1
    assert body["sync"]["successful"] == 1
    assert body["sync"]["failed"] == 0
    assert body["sync"]["healthy"] is True
    assert "demo" in body["sync"]["last_success"]
