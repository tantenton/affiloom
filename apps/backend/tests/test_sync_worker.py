"""Smoke test for the sync worker CLI entrypoint."""

from __future__ import annotations

import json

import pytest

from workers import sync_worker


@pytest.mark.asyncio
async def test_worker_one_shot_runs_sync(initialized_db: str, capsys) -> None:
    """One-shot invocation exits 0 and prints a JSON summary."""
    exit_code = await sync_worker.main_async(
        sync_worker.build_parser().parse_args(["--max-retries", "1"])
    )
    assert exit_code == 0
    captured = capsys.readouterr().out.strip()
    payload = json.loads(captured)
    assert payload["merchant"] == "demo"
    assert payload["status"] == "success"
    assert payload["seen"] == 10
    assert payload["created"] == 10