"""Integration smoke tests: health, catalog, content against the live app.

These are designed to run against a running backend (localhost:8000).
They validate the full HTTP path — middleware, routing, serialisation — that
the per-module unit tests cannot cover.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio

BACKEND_URL = "http://localhost:8000"


@pytest.mark.integration
class TestHealthSmoke:
    async def test_health_liveness(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"

    async def test_readiness(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/ready")
        assert r.status_code in (200, 503)
        data = r.json()
        assert "status" in data
        assert "deps" in data

    async def test_deps_shape(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/deps")
        assert r.status_code == 200
        names = {d["name"] for d in r.json()["deps"]}
        assert "database" in names


@pytest.mark.integration
class TestCatalogSmoke:
    async def test_list_products(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/products")
        assert r.status_code == 200
        body = r.json()
        assert "items" in body
        assert body["total"] >= 10

    async def test_product_detail(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/products/demo-1")
        assert r.status_code == 200
        assert r.json()["id"] == "demo-1"

    async def test_product_search(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/products?q=kopi")
        assert r.status_code == 200
        ids = {i["id"] for i in r.json()["items"]}
        assert "demo-4" in ids  # Kopi Arabika Gayo

    async def test_product_404(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/products/nonexistent-xyz")
        assert r.status_code == 404


@pytest.mark.integration
class TestContentSmoke:
    async def test_sitemap_static_entries(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/sitemap")
        assert r.status_code == 200
        locs = [e["loc"] for e in r.json()["entries"]]
        assert "/" in locs
        assert "/produk" in locs

    async def test_robots(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/robots")
        assert r.status_code == 200
        assert "/sitemap.xml" in r.json()["sitemaps"]

    async def test_current_site(self, client: httpx.AsyncClient) -> None:
        r = await client.get("/api/sites/current")
        assert r.status_code == 200
        assert r.json()["slug"] == "affiloom"


@pytest_asyncio.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(base_url=BACKEND_URL, timeout=5) as c:
        yield c
