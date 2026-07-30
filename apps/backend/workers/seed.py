"""Seed the database with the deterministic demo catalog.

Idempotent: re-running is a no-op. Validates that the sync service
upserts without errors and the data model is consistent.

Usage:
    cd apps/backend
    DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic upgrade head
    DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run python -m workers.seed

The first run creates 10 products and offers. The second run
produces identical counters with ``created=0``.
"""

from __future__ import annotations

import json
import sys

from db.session import get_sessionmaker
from dependencies import get_catalog_adapter
from services.logging import setup_logging
from services.search import InMemoryIndexer
from services.sync import run_sync

setup_logging("INFO")


def main() -> int:
    adapter = get_catalog_adapter()
    indexer = InMemoryIndexer()
    factory = get_sessionmaker()

    import asyncio

    async def _run() -> int:
        async with factory() as session:
            result = await run_sync(session, adapter=adapter, indexer=indexer,  # noqa: E501
                trigger="seed")

        print(json.dumps({
            "run_id": result.run_id,
            "merchant": result.merchant_slug,
            "status": result.status.value,
            "seen": result.seen,
            "created": result.created,
            "updated": result.updated,
            "deactivated": result.deactivated,
            "skipped": result.skipped,
            "error": result.error,
        }))

        return 0 if result.status.value in ("success", "pending") else 1

    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
