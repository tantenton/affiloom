"""Admin /api/admin/content endpoints: sites, categories, drafts, publish, links."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from adapters.provider import DeterministicDemoAdapter, demo_items
from config import settings
from dependencies import get_catalog_adapter
from main import app


@pytest.fixture()
def admin_client(initialized_db: str, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "test-admin-token")
    # AI stays disabled for these tests; default deterministic path exercised.
    monkeypatch.setattr(settings, "CONTENT_AI_ENABLED", False)

    def _adapter() -> DeterministicDemoAdapter:
        return DeterministicDemoAdapter({i.id: i for i in demo_items()})

    app.dependency_overrides[get_catalog_adapter] = _adapter
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_catalog_adapter, None)


def _h() -> dict[str, str]:
    return {"Authorization": "Bearer test-admin-token"}


def test_create_site_requires_token(admin_client: TestClient) -> None:
    r = admin_client.post(
        "/api/admin/content/sites",
        json={"slug": "s1", "domain": "s1.test", "name": "Site 1"},
    )
    assert r.status_code == 401


def test_end_to_end_content_workflow(admin_client: TestClient) -> None:
    # Sync products first so link-suggestion has real data.
    admin_client.post("/api/admin/sync/demo", headers=_h())

    r = admin_client.post(
        "/api/admin/content/sites",
        json={"slug": "affiloom", "domain": "affiloom.test", "name": "Affiloom"},
        headers=_h(),
    )
    assert r.status_code == 200, r.text
    site = r.json()
    assert site["slug"] == "affiloom"

    r = admin_client.post(
        "/api/admin/content/categories",
        json={
            "site_slug": "affiloom",
            "slug": "fashion",
            "name": "Fashion",
            "description": "Kategori fashion.",
        },
        headers=_h(),
    )
    assert r.status_code == 200, r.text
    cat = r.json()
    assert cat["slug"] == "fashion"

    # Draft an Indonesian article with a Fashion keyword.
    r = admin_client.post(
        "/api/admin/content/drafts",
        json={
            "site_slug": "affiloom",
            "category_slug": "fashion",
            "title": "Panduan Memilih Tas Kanvas Ramah Lingkungan",
            "target_keyword": "tas kanvas",
            "related_product_ids": ["demo-1"],
            "use_ai": False,
        },
        headers=_h(),
    )
    assert r.status_code == 200, r.text
    draft = r.json()
    assert draft["status"] == "draft"
    assert draft["slug"] == "panduan-memilih-tas-kanvas-ramah-lingkungan"
    assert draft["canonical_path"].startswith("/artikel/")
    assert draft["language"] == "id-ID"
    assert "tas" in draft["body_md"].lower()

    article_id = draft["id"]

    # Internal link suggestions from token overlap.
    r = admin_client.get(
        f"/api/admin/content/articles/{article_id}/link-suggestions",
        headers=_h(),
    )
    assert r.status_code == 200
    suggestions = r.json()["suggestions"]
    # We linked demo-1 and topic mentions 'tas' + 'kanvas' — expect at least one.
    assert len(suggestions) >= 1
    assert all("score" in s for s in suggestions)
    top = suggestions[0]
    assert top["score"] > 0

    # Publish moves it to 'published'.
    r = admin_client.post(
        f"/api/admin/content/articles/{article_id}/publish", headers=_h()
    )
    assert r.status_code == 200, r.text
    pub = r.json()
    assert pub["status"] == "published"
    assert pub["published_at"] is not None

    # Public list now shows exactly this article.
    r = admin_client.get("/api/articles")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == draft["slug"]
    assert body["items"][0]["status"] == "published"

    # Public detail includes JSON-LD-ready shape + linked products.
    r = admin_client.get(f"/api/articles/{draft['slug']}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["title"] == draft["title"]
    assert detail["category"]["slug"] == "fashion"
    product_ids = [p["external_id"] for p in detail["products"]]
    assert "demo-1" in product_ids

    # Filter articles by category slug.
    r = admin_client.get("/api/articles?category=fashion")
    assert r.status_code == 200
    assert r.json()["total"] == 1
    r = admin_client.get("/api/articles?category=kuliner")
    assert r.json()["total"] == 0

    # Category detail exposes count of published articles.
    r = admin_client.get("/api/categories/fashion")
    assert r.status_code == 200
    assert r.json()["article_count"] == 1

    # Sitemap picks up the new article + category.
    r = admin_client.get("/api/sitemap")
    locs = [e["loc"] for e in r.json()["entries"]]
    assert f"/artikel/{draft['slug']}" in locs
    assert "/kategori/fashion" in locs


def test_publish_missing_article_returns_404(admin_client: TestClient) -> None:
    r = admin_client.post(
        "/api/admin/content/articles/does-not-exist/publish", headers=_h()
    )
    assert r.status_code == 404


def test_draft_with_ai_disabled_falls_back_to_deterministic(
    admin_client: TestClient, monkeypatch
) -> None:
    """When CONTENT_AI_ENABLED=False and use_ai=True the request must fail closed."""  # noqa: E501
    monkeypatch.setattr(settings, "CONTENT_AI_ENABLED", False)
    admin_client.post(
        "/api/admin/content/sites",
        json={"slug": "affiloom", "domain": "affiloom.test", "name": "Affiloom"},
        headers=_h(),
    )
    admin_client.post(
        "/api/admin/content/categories",
        json={"site_slug": "affiloom", "slug": "fashion", "name": "Fashion"},
        headers=_h(),
    )
    r = admin_client.post(
        "/api/admin/content/drafts",
        json={
            "site_slug": "affiloom",
            "category_slug": "fashion",
            "title": "Draft dengan AI Diminta",
            "target_keyword": "kanvas",
            "use_ai": True,
        },
        headers=_h(),
    )
    # AI is disabled: router must fail closed with 503, not silently
    # fall back to deterministic content or fabricate output.
    assert r.status_code == 503
    assert "disabled" in r.json()["detail"].lower()
