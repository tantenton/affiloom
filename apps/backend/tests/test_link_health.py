"""Tests for link health checking service (M5-003)."""

from __future__ import annotations

from services.link_health import validate_url_format


def test_validate_url_format() -> None:
    ok, err = validate_url_format("https://example.com/path?foo=bar")
    assert ok is True
    assert err is None

    ok, err = validate_url_format("javascript:alert(1)")
    assert ok is False
    assert err is not None
