"""Tests for the /api/products list/search + detail endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_list_products_returns_paginated_envelope() -> None:
    response = client.get("/api/products")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"items", "total", "limit", "offset", "query"}
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert body["query"] is None
    assert body["total"] == 10
    assert len(body["items"]) == 10

    first = body["items"][0]
    assert first["id"] == "demo-1"
    for required in ("id", "source", "title", "url", "price", "currency"):
        assert required in first


def test_list_products_deterministic_order() -> None:
    a = client.get("/api/products").json()["items"]
    b = client.get("/api/products").json()["items"]
    assert [x["id"] for x in a] == [x["id"] for x in b]


def test_list_products_limit_and_offset() -> None:
    body = client.get("/api/products?limit=3&offset=2").json()
    assert body["limit"] == 3
    assert body["offset"] == 2
    assert len(body["items"]) == 3
    assert body["items"][0]["id"] == "demo-3"


def test_list_products_search_filter_case_insensitive() -> None:
    body = client.get("/api/products?q=BOTOL").json()
    ids = [item["id"] for item in body["items"]]
    assert "demo-2" in ids
    assert body["query"] == "BOTOL"
    for item in body["items"]:
        assert "botol" in item["title"].lower() or (
            item.get("category") and "botol" in item["category"].lower()
        )


def test_list_products_search_matches_category() -> None:
    body = client.get("/api/products?q=Fashion").json()
    ids = {item["id"] for item in body["items"]}
    assert {"demo-1", "demo-3"}.issubset(ids)
    assert body["total"] >= 2


def test_list_products_empty_result_when_no_match() -> None:
    body = client.get("/api/products?q=zzzz-no-match").json()
    assert body["total"] == 0
    assert body["items"] == []


def test_list_products_rejects_invalid_limit() -> None:
    assert client.get("/api/products?limit=0").status_code == 422
    assert client.get("/api/products?limit=101").status_code == 422
    assert client.get("/api/products?limit=-1").status_code == 422


def test_list_products_rejects_invalid_offset() -> None:
    assert client.get("/api/products?offset=-1").status_code == 422


def test_product_detail_returns_full_payload() -> None:
    response = client.get("/api/products/demo-1")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "demo-1"
    assert body["title"] == "Tas Jinjing Kanvas Eco"
    assert body["price"] == 125000.0
    assert body["currency"] == "IDR"
    assert body["category"] == "Fashion"
    assert body["url"].startswith("https://")
    assert body["image_url"].startswith("https://")
    assert body["description"]


def test_compare_returns_products_and_missing_ids() -> None:
    response = client.get("/api/products/compare?ids=demo-1&ids=demo-2&ids=missing")
    assert response.status_code == 200
    body = response.json()
    assert [item["id"] for item in body["products"]] == ["demo-1", "demo-2"]
    assert body["missing"] == ["missing"]


def test_compare_rejects_more_than_four_ids() -> None:
    ids = "&".join(f"ids=demo-{number}" for number in range(1, 6))
    response = client.get(f"/api/products/compare?{ids}")
    assert response.status_code == 422


def test_product_detail_404_shape() -> None:
    response = client.get("/api/products/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Product not found"


@pytest.mark.parametrize(
    "bad_id",
    [
        "UPPERCASE",
        "has_space",
        "../etc/passwd",
        "a" * 129,
        "!@#",
    ],
)
def test_product_detail_rejects_invalid_id(bad_id: str) -> None:
    response = client.get(f"/api/products/{bad_id}")
    # Router refuses ids that don't match ^[a-z0-9][a-z0-9-]{0,127}$; Starlette
    # returns 422 for its own length caps.
    assert response.status_code in (404, 422)
