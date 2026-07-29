"""Tests for the /api/admin sync endpoints.

Runs against a per-test SQLite DB with tables created and the FastAPI app
mounted through a TestClient. We swap the admin token and the ``settings``
so the guard exercises the real auth path.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adapters.provider import DeterministicDemoAdapter, demo_items
from config import settings
from dependencies import get_catalog_adapter
from main import app
from services.search import reset_indexer


@pytest.fixture()
def admin_client(initialized_db: str, monkeypatch):
    """TestClient with admin token set + adapter override to a fresh seed."""
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "test-admin-token")
    reset_indexer()

    def _adapter() -> DeterministicDemoAdapter:
        return DeterministicDemoAdapter({i.id: i for i in demo_items()})

    app.dependency_overrides[get_catalog_adapter] = _adapter
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_catalog_adapter, None)


def _auth() -> dict[str, str]:
    return {"Authorization": "Bearer test-admin-token"}


def test_admin_requires_token(admin_client: TestClient) -> None:
    r = admin_client.post("/api/admin/sync/demo")
    assert r.status_code == 401


def test_admin_rejects_wrong_token(admin_client: TestClient) -> None:
    r = admin_client.post(
        "/api/admin/sync/demo", headers={"Authorization": "Bearer nope"}
    )
    assert r.status_code == 403


def test_admin_503_when_token_not_configured(
    initialized_db: str, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "")
    with TestClient(app) as client:
        r = client.post(
            "/api/admin/sync/demo", headers={"Authorization": "Bearer anything"}
        )
    assert r.status_code == 503


def test_admin_trigger_sync_creates_run(admin_client: TestClient) -> None:
    r = admin_client.post("/api/admin/sync/demo", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["merchant"] == "demo"
    assert body["status"] == "success"
    assert body["seen"] == 10
    assert body["created"] == 10
    assert body["updated"] == 0
    assert body["deactivated"] == 0
    assert body["skipped"] is False
    assert body["run_id"]


def test_admin_trigger_unknown_merchant_404(admin_client: TestClient) -> None:
    r = admin_client.post("/api/admin/sync/shopee", headers=_auth())
    assert r.status_code == 404


def test_admin_list_runs_returns_history(admin_client: TestClient) -> None:
    for _ in range(2):
        r = admin_client.post("/api/admin/sync/demo", headers=_auth())
        assert r.status_code == 200

    r = admin_client.get("/api/admin/sync/runs", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["merchant_slug"] == "demo"
    assert body["items"][0]["status"] == "success"


def test_admin_get_run_detail(admin_client: TestClient) -> None:
    trigger = admin_client.post("/api/admin/sync/demo", headers=_auth()).json()
    run_id = trigger["run_id"]

    r = admin_client.get(f"/api/admin/sync/runs/{run_id}", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == run_id
    assert body["merchant_slug"] == "demo"
    assert body["products_seen"] == 10
    assert body["stats"] is not None
    assert body["stats"]["adapter"] == "demo"


def test_admin_get_run_detail_404(admin_client: TestClient) -> None:
    r = admin_client.get("/api/admin/sync/runs/does-not-exist", headers=_auth())
    assert r.status_code == 404
