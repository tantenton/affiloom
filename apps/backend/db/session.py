"""Async engine + sessionmaker plumbing.

Exposed helpers:

* ``get_engine()`` — lazy singleton engine derived from ``settings.DATABASE_URL``.
* ``get_sessionmaker()`` — lazy singleton ``async_sessionmaker`` bound to the
  engine above.
* ``get_session()`` — FastAPI dependency yielding an ``AsyncSession``.
* ``reset_engine()`` — clear caches (used by tests that swap DB URLs).
* ``dispose_engine()`` — close the pool cleanly on shutdown.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings


def _normalize_url(url: str) -> str:
    """Ensure the URL uses an async driver.

    * ``sqlite://`` becomes ``sqlite+aiosqlite://`` so tests can point at
      ``sqlite:///:memory:`` or a temp file without picking the sync driver.
    * ``postgresql://`` becomes ``postgresql+asyncpg://`` when a driver hasn't
      been declared. Explicit ``postgresql+psycopg`` values are left alone.
    """
    if url.startswith("sqlite+"):
        return url
    if url.startswith("sqlite://"):
        return "sqlite+aiosqlite://" + url[len("sqlite://") :]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    url = _normalize_url(settings.DATABASE_URL)
    connect_args: dict = {}
    kwargs: dict = {"pool_pre_ping": True, "future": True}
    if url.startswith("sqlite+aiosqlite"):
        # In-memory + StaticPool would keep state across sessions but breaks
        # concurrent tests; caller supplies a file: URL when persistence is
        # desired. This branch just disables SQLite's thread check.
        connect_args["check_same_thread"] = False
        kwargs.pop("pool_pre_ping", None)
    return create_async_engine(url, connect_args=connect_args, **kwargs)


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields a session, rolls back on error."""
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def reset_engine() -> None:
    """Clear cached engine + sessionmaker.

    Tests call this after mutating ``settings.DATABASE_URL`` to force the
    next ``get_engine`` call to rebuild against the new URL.
    """
    get_engine.cache_clear()
    get_sessionmaker.cache_clear()


async def dispose_engine() -> None:
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
    reset_engine()


__all__ = [
    "dispose_engine",
    "get_engine",
    "get_session",
    "get_sessionmaker",
    "reset_engine",
]
