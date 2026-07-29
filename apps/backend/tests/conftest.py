"""Shared pytest fixtures.

Every DB-touching test gets its own SQLite temp file so runs stay parallel-
friendly and isolated. The engine is rebuilt via ``reset_engine`` after we
mutate ``settings.DATABASE_URL`` so lazy caches don't leak across tests.
"""

from __future__ import annotations

import os
import sys
from collections.abc import AsyncIterator
from pathlib import Path

import pytest_asyncio

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


@pytest_asyncio.fixture()
async def db_url(tmp_path: Path) -> AsyncIterator[str]:
    """Set ``DATABASE_URL`` to a per-test SQLite file and yield the URL."""
    from config import settings
    from db.session import dispose_engine, reset_engine
    from services.search import reset_indexer

    db_path = tmp_path / "affiloom-test.db"
    url = f"sqlite+aiosqlite:///{db_path}"

    original = settings.DATABASE_URL
    os.environ["DATABASE_URL"] = url
    settings.DATABASE_URL = url
    reset_engine()
    reset_indexer()

    try:
        yield url
    finally:
        await dispose_engine()
        settings.DATABASE_URL = original
        os.environ.pop("DATABASE_URL", None)
        reset_engine()
        reset_indexer()


@pytest_asyncio.fixture()
async def initialized_db(db_url: str) -> AsyncIterator[str]:
    """Create all tables on the per-test SQLite file."""
    from db.models import Base
    from db.session import get_engine

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield db_url
