"""Structured JSON-line logging for the Affiloom backend.

Every log line emitted through this module is a single-line JSON object with
at minimum the keys ``ts``, ``svc``, ``level``, and ``msg``.  Contextual
fields are passed via the standard ``extra`` dict and merged into the record
so downstream log aggregators (Datadog, Loki, ELK) can index fields without
Grok patterns.

Usage
-----
    from services.logging import get_logger
    log = get_logger(__name__)

    log.info("sync: started", extra={"merchant": "demo", "run_id": "..."})
    # {"ts":"...","svc":"services.sync","level":"INFO","msg":"sync: started","merchant":"demo","run_id":"..."}
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    _RESERVED = frozenset({
        "name", "msg", "args", "levelname", "levelno", "pathname",
        "filename", "module", "exc_info", "exc_text", "stack_info",
        "lineno", "funcName", "created", "msecs", "relativeCreated",
        "thread", "threadName", "processName", "process", "taskName",
        "message",
    })

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "svc": record.name,
            "level": record.levelname,
            "msg": record.getMessage(),
        }

        # Merge extra fields: anything on the record not reserved becomes context.
        for key in vars(record):
            if key.startswith("_"):
                continue
            if key in self._RESERVED:
                continue
            payload[key] = getattr(record, key)

        if record.exc_info and record.exc_info[1]:
            payload["exc"] = repr(record.exc_info[1])

        return json.dumps(payload, default=str, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    """Return a logger configured for structured JSON output.

    Contextual fields are passed via ``extra={"key": value}`` and merged
    into the JSON record by the formatter.
    """
    return logging.getLogger(name)


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger with a structured JSON stream handler.

    Call once at startup before any logging.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level.upper(), logging.INFO))