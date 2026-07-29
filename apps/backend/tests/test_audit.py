"""Tests for the daily audit service and admin audit endpoint."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import Article, ArticleStatus, Merchant, SyncRun, SyncRunStatus
from db.session import get_sessionmaker
from main import app
from services.audit import run_audit
from services.search import reset_indexer


@pytest.fixture()
def admin_client(initialized_db: str, monkeypatch):
    monkeypatch.setattr(settings, "ADMIN_API_TOKEN", "test-admin-token")
    reset_indexer()
    with TestClient(app) as client:
        yield client


def _auth() -> dict[str, str]:
    return {"Authorization": "Bearer test-admin-token"}


@pytest.mark.asyncio
async def test_audit_empty_db(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        findings = await run_audit(session)

    # Empty DB: no merchants → no merchant-without-success findings,
    # but also no failures. Should be 0 findings.
    assert findings == []


@pytest.mark.asyncio
async def test_audit_detects_no_successful_sync(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        merchant = Merchant(slug="demo", display_name="Demo", is_active=True)
        session.add(merchant)
        await session.commit()

        findings = await run_audit(session)

    # Should flag: merchant has no successful sync
    messages = [f.message for f in findings]
    assert any("no successful sync" in m for m in messages)


@pytest.mark.asyncio
async def test_audit_detects_failed_sync(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        merchant = Merchant(slug="demo", display_name="Demo", is_active=True)
        session.add(merchant)
        await session.flush()

        run = SyncRun(
            merchant_id=merchant.id,
            status=SyncRunStatus.FAILED,
            trigger="worker",
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
            error="adapter timeout",
        )
        session.add(run)
        await session.commit()

        findings = await run_audit(session)

    messages = [f.message for f in findings]
    assert any("failed" in m.lower() for m in messages)


@pytest.mark.asyncio
async def test_audit_detects_stale_sync(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        merchant = Merchant(slug="demo", display_name="Demo", is_active=True)
        session.add(merchant)
        await session.flush()

        old_time = datetime.now(timezone.utc) - timedelta(days=10)
        run = SyncRun(
            merchant_id=merchant.id,
            status=SyncRunStatus.SUCCESS,
            trigger="worker",
            started_at=old_time,
            finished_at=old_time,
        )
        session.add(run)
        await session.commit()

        findings = await run_audit(session)

    messages = [f.message for f in findings]
    assert any("last synced" in m.lower() for m in messages)


@pytest.mark.asyncio
async def test_audit_detects_stuck_run(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        merchant = Merchant(slug="demo", display_name="Demo", is_active=True)
        session.add(merchant)
        await session.flush()

        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        run = SyncRun(
            merchant_id=merchant.id,
            status=SyncRunStatus.RUNNING,
            trigger="worker",
            started_at=old_time,
        )
        session.add(run)
        await session.commit()

        findings = await run_audit(session)

    messages = [f.message for f in findings]
    assert any("stuck" in m.lower() for m in messages)


@pytest.mark.asyncio
async def test_audit_detects_missing_excerpt(initialized_db: str) -> None:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        from db.models import Site

        site = Site(slug="affiloom", domain="localhost", name="Affiloom")
        session.add(site)
        await session.flush()

        article = Article(
            site_id=site.id,
            slug="test-slug",
            title="Test Article",
            body_md="content",
            status=ArticleStatus.PUBLISHED,
            excerpt=None,
            meta_description=None,
            published_at=datetime.now(timezone.utc),
        )
        session.add(article)
        await session.commit()

        findings = await run_audit(session)

    categories = [f.category for f in findings]
    assert "content.seo" in categories


def test_admin_audit_endpoint(admin_client: TestClient) -> None:
    r = admin_client.get("/api/admin/audit", headers=_auth())
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "critical" in body
    assert "warning" in body
    assert "info" in body
    assert isinstance(body["findings"], list)
