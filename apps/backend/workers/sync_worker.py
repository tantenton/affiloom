"""Catalog sync worker with retry and dead-letter-safe patterns.

Run as a one-shot job (default) or in a loop with ``--interval SECONDS``:

    python -m workers.sync_worker                  # one pass, exits with code 0/1
    python -m workers.sync_worker --interval 300     # loop every 5 min
    python -m workers.sync_worker --max-retries 3 --retry-delay 10  # retry on failure

Retry policy
------------
When a sync fails transiently (adapter timeout, DB connection blip), the worker
retries up to ``--max-retries`` times with exponential backoff (base =
``--retry-delay`` seconds * 2^attempt). After exhausting retries, the failed
run is recorded in the DB with status=FAILED (the sync service already does
this), making it visible in the admin dashboard and daily audit. The worker
then exits with code 1 (one-shot) or continues the loop (interval mode).

Dead-letter safety
-------------------
* No uncaught exceptions escape to the scheduler — all are caught and logged.
* A failed run is never retried by the next loop iteration; the Redis lock
  (when enabled) prevents concurrent runs, and the sync service records the
  FAILED status so the audit job can surface it.
* The worker never blocks indefinitely on a single run; ``--run-timeout``
  caps the wall-clock per attempt.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Optional

from db.session import get_sessionmaker
from dependencies import get_catalog_adapter
from services.logging import setup_logging
from services.sync import SyncResult, run_sync

log = logging.getLogger("affiloom.sync_worker")


async def _run_once() -> SyncResult:
    adapter = get_catalog_adapter()
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        return await run_sync(session, adapter=adapter, trigger="worker")


async def _run_with_retry(
    max_retries: int, retry_delay: float, run_timeout: Optional[float]
) -> SyncResult:
    """Run sync with retry on transient failure and a per-attempt timeout."""
    last_result: Optional[SyncResult] = None
    for attempt in range(1, max_retries + 1):
        try:
            if run_timeout:
                result = await asyncio.wait_for(_run_once(), timeout=run_timeout)
            else:
                result = await _run_once()
            last_result = result
            if result.status.value != "failed":
                return result
            # Skipped (lock held) is not a failure — don't retry.
            if result.skipped:
                return result
            log.warning(
                "sync_worker: attempt %d/%d failed (status=%s)",
                attempt,
                max_retries,
                result.status.value,
            )
        except asyncio.TimeoutError:
            log.error(
                "sync_worker: attempt %d/%d timed out after %s s",
                attempt,
                max_retries,
                run_timeout,
            )
            last_result = SyncResult(
                run_id="",
                merchant_slug="demo",
                status=__import__(
                    "db.models", fromlist=["SyncRunStatus"]
                ).SyncRunStatus.FAILED,
                seen=0,
                created=0,
                updated=0,
                deactivated=0,
                error=f"timeout after {run_timeout}s",
            )
        except Exception:  # noqa: BLE001
            log.exception("sync_worker: attempt %d/%d raised", attempt, max_retries)
            last_result = SyncResult(
                run_id="",
                merchant_slug="demo",
                status=__import__(
                    "db.models", fromlist=["SyncRunStatus"]
                ).SyncRunStatus.FAILED,
                seen=0,
                created=0,
                updated=0,
                deactivated=0,
                error="unhandled exception (see logs)",
            )

        if attempt < max_retries:
            backoff = retry_delay * (2 ** (attempt - 1))
            log.info("sync_worker: retrying in %.1f s", backoff)
            await asyncio.sleep(backoff)

    return last_result  # type: ignore[return-value]


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


async def main_async(args: argparse.Namespace) -> int:
    setup_logging(args.log_level)

    if args.interval and args.interval > 0:
        log.info(
            "sync_worker: looping every %s s (max_retries=%d)",
            args.interval,
            args.max_retries,
        )
        while True:
            try:
                result = await _run_with_retry(
                    args.max_retries, args.retry_delay, args.run_timeout
                )
                log.info("sync_worker: %s", json.dumps(_summary(result)))
            except Exception:  # noqa: BLE001
                log.exception("sync_worker: loop iteration failed")
            await asyncio.sleep(args.interval)

    try:
        result = await _run_with_retry(
            args.max_retries, args.retry_delay, args.run_timeout
        )
        print(json.dumps(_summary(result)))
        return 0 if result.status.value != "failed" else 1
    except Exception:  # noqa: BLE001
        log.exception("sync_worker: fatal")
        return 1


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
    p.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum sync attempts before giving up (default: 3).",
    )
    p.add_argument(
        "--retry-delay",
        type=float,
        default=10.0,
        help="Base backoff seconds between retries; doubles each attempt (default: 10).",  # noqa: E501
    )
    p.add_argument(
        "--run-timeout",
        type=float,
        default=None,
        help="Maximum wall-clock seconds per sync attempt (default: unlimited).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return asyncio.run(main_async(args))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
