"""Daily audit worker.

Runs the audit service and emits findings as JSON to stdout.

    python -m workers.audit_worker                  # one-shot
    python -m workers.audit_worker --interval 86400  # daily loop

The worker is dead-letter-safe: failures are caught, logged with structured
context, and the exit code reflects failure. It never raises uncaught
exceptions to the scheduler.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys

from db.session import get_sessionmaker
from services.audit import finding_to_dict, run_audit
from services.logging import setup_logging

log = logging.getLogger("affiloom.audit_worker")


async def _run_once() -> dict:
    session_factory = get_sessionmaker()
    async with session_factory() as session:
        findings = await run_audit(session)

    return {
        "checked_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "total_findings": len(findings),
        "critical": sum(1 for f in findings if f.severity.value == "critical"),
        "warning": sum(1 for f in findings if f.severity.value == "warning"),
        "info": sum(1 for f in findings if f.severity.value == "info"),
        "findings": [finding_to_dict(f) for f in findings],
    }


async def main_async(args: argparse.Namespace) -> int:
    setup_logging(args.log_level)

    if args.interval and args.interval > 0:
        log.info("audit_worker: looping every %s s", args.interval)
        while True:
            try:
                result = await _run_once()
                log.info(
                    "audit_worker: completed",
                )
                print(json.dumps(result))
            except Exception:  # noqa: BLE001
                log.exception("audit_worker: run failed")
            await asyncio.sleep(args.interval)

    try:
        result = await _run_once()
        print(json.dumps(result))
        return 0 if result["critical"] == 0 else 1
    except Exception:  # noqa: BLE001
        log.exception("audit_worker: fatal")
        return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Affiloom daily audit worker")
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
    return asyncio.run(main_async(args))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
