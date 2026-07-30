"""Tests for structured JSON logging."""

from __future__ import annotations

import json

from services.logging import get_logger, setup_logging


def _read_log(capsys) -> str:
    captured = capsys.readouterr()
    # Logs go to stderr; data goes to stdout.
    return (captured.err or captured.out).strip()


def test_structured_log_emits_json(capsys) -> None:
    setup_logging("INFO")
    log = get_logger("test.module")
    log.info("sync started", extra={"merchant": "demo", "run_id": "abc123"})

    parsed = json.loads(_read_log(capsys))
    assert parsed["svc"] == "test.module"
    assert parsed["level"] == "INFO"
    assert parsed["msg"] == "sync started"
    assert parsed["merchant"] == "demo"
    assert parsed["run_id"] == "abc123"
    assert "ts" in parsed


def test_structured_log_warning(capsys) -> None:
    setup_logging("WARNING")
    log = get_logger("test.warn")
    log.warning("slow query", extra={"query": "SELECT 1", "duration_ms": 500})

    parsed = json.loads(_read_log(capsys))
    assert parsed["level"] == "WARNING"
    assert parsed["query"] == "SELECT 1"
    assert parsed["duration_ms"] == 500


def test_structured_log_exception(capsys) -> None:
    setup_logging("ERROR")
    log = get_logger("test.exc")
    try:
        raise ValueError("boom")
    except ValueError:
        log.exception("caught error", extra={"context": "sync"})

    parsed = json.loads(_read_log(capsys))
    assert parsed["level"] == "ERROR"
    assert parsed["msg"] == "caught error"
    assert parsed["context"] == "sync"
    assert "boom" in parsed["exc"]
