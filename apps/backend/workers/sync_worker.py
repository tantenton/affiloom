"""Catalog sync worker.

Run as a one-shot job (default) or in a loop with ``--interval SECONDS``:

    python -m workers.sync_worker              # one pass, exits with code 0/1
    python -m workers.sync_worker --interval 300  # loop every 5 min

The worker uses the same ``run_sync`` service the admin endpoint calls, so
the code path is deterministic and identical across triggers.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

from db.session import get_sessionmaker
from dependencies import get_catalog_adapter
from services.sync import SyncResult, run_sync

log = logging.getLogger("affiloom.sync_worker")


async def _run_once() -> SyncResult:
    adapter = get_catalog_adapter()
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        return await run_sync(session, adapter=adapter, trigger="worker")


async def main_async(args: argparse.Namespace) -> int:
    if args.interval and args.interval > 0:
        log.info("sync_worker: looping every %s s", args.interval)
        while True:
            result = await _run_once()
            log.info("sync_worker: %s", _summary(result))
            await asyncio.sleep(args.interval)
    result = await _run_once()
    print(json.dumps(_summary(result)))
    return 0 if result.status.value != "failed" else 1


def _summary(result: SyncResult) -> dict:
    return {
        "run_id": result.run_id,
        "merchant": result.merchant_slug,
        "status": result.status.value,
        "seen": result.seen,
        "created": result.created,
        "updated": result.updated,
        "deactivated": result.deactivated,
        "skipped": result.skipped,
        "error": result.error,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Affiloom catalog sync worker")
    p.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Seconds between runs; 0 (default) runs exactly once and exits.",
    )
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return asyncio.run(main_async(args))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
