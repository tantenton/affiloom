"""Public /api/sites, /api/categories, /api/articles read layer tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture()
def public_client(initialized_db: str):
    with TestClient(app) as client:
        yield client


def test_current_site_returns_default_when_empty(public_client: TestClient) -> None:
    r = public_client.get("/api/sites/current")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "affiloom"
    assert body["language"] == "id-ID"


def test_categories_empty_when_no_content(public_client: TestClient) -> None:
    r = public_client.get("/api/categories")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_articles_empty_when_no_content(public_client: TestClient) -> None:
    r = public_client.get("/api/articles")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 20
    assert body["category"] is None


def test_article_not_found(public_client: TestClient) -> None:
    r = public_client.get("/api/articles/tidak-ada")
    assert r.status_code == 404
    assert r.json()["detail"] == "Article not found"


def test_category_not_found(public_client: TestClient) -> None:
    r = public_client.get("/api/categories/tidak-ada")
    assert r.status_code == 404


def test_sitemap_lists_products_and_static_pages(public_client: TestClient) -> None:
    r = public_client.get("/api/sitemap")
    assert r.status_code == 200
    body = r.json()
    locs = [entry["loc"] for entry in body["entries"]]
    assert "/" in locs
    assert "/produk" in locs
    assert "/artikel" in locs
    assert "/produk/demo-1" in locs
    for entry in body["entries"]:
        assert entry["loc"].startswith("/")
        assert "changefreq" in entry
        assert "priority" in entry


def test_robots_directive_shape(public_client: TestClient) -> None:
    r = public_client.get("/api/robots")
    assert r.status_code == 200
    body = r.json()
    assert body["sitemaps"] == ["/sitemap.xml"]
    rule = body["rules"][0]
    assert rule["user_agent"] == "*"
    assert rule["allow"] == "/"
    assert "/api/admin/" in rule["disallow"]
