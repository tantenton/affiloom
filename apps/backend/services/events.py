"""Best-effort Redis lock + RabbitMQ event publishing.

Neither is required for the sync service to complete: if the daemon is
disabled via env or unreachable the helpers degrade gracefully so tests and
offline runs stay green.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from config import settings

log = logging.getLogger(__name__)


class _AlwaysAcquiredLock:
    """Fallback lock used when Redis is disabled or unreachable."""

    async def __aenter__(self) -> "_AlwaysAcquiredLock":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None


@asynccontextmanager
async def sync_lock(name: str, *, ttl: int = 300) -> AsyncIterator[bool]:
    """Try to acquire a distributed Redis lock; yield True on success.

    * Yields ``True`` and holds the lock if Redis is enabled and reachable.
    * Yields ``True`` with the fallback lock if Redis is disabled.
    * Yields ``False`` if another worker already holds the lock (only possible
      when Redis is enabled and reachable).
    """
    if not settings.REDIS_ENABLED:
        async with _AlwaysAcquiredLock():
            yield True
        return

    try:
        import redis.asyncio as aioredis  # imported lazily so tests don't pay
    except Exception:  # noqa: BLE001
        log.warning("events: redis client unavailable; running without lock")
        async with _AlwaysAcquiredLock():
            yield True
        return

    client = aioredis.from_url(settings.REDIS_URL)
    key = f"affiloom:sync:{name}"
    token = str(asyncio.current_task())
    try:
        acquired = await client.set(key, token, nx=True, ex=ttl)
    except Exception as exc:  # noqa: BLE001
        log.warning("events: redis unreachable (%s); running without lock", exc)
        async with _AlwaysAcquiredLock():
            yield True
        await client.aclose()
        return

    if not acquired:
        log.info("events: sync lock %s already held; skipping", name)
        yield False
        await client.aclose()
        return

    try:
        yield True
    finally:
        try:
            # Only release if we still own the token.
            current = await client.get(key)
            if current == token.encode() or current == token:
                await client.delete(key)
        except Exception:  # noqa: BLE001
            pass
        await client.aclose()


async def publish_sync_event(payload: dict) -> Optional[str]:
    """Publish a ``sync.completed`` event to RabbitMQ.

    Returns the exchange name on success, ``None`` when publishing is skipped
    or fails. Never raises: sync completion is the source of truth, events
    are advisory.
    """
    if not settings.RABBITMQ_ENABLED:
        return None
    try:
        import aio_pika
    except Exception:  # noqa: BLE001
        log.warning("events: aio_pika unavailable; skipping publish")
        return None

    try:
        connection = await aio_pika.connect_robust(settings.RABBITMQ_URL, timeout=5)
    except Exception as exc:  # noqa: BLE001
        log.warning("events: rabbitmq unreachable (%s); skipping publish", exc)
        return None

    try:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            settings.RABBITMQ_EXCHANGE,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        message = aio_pika.Message(
            body=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=settings.RABBITMQ_ROUTING_KEY)
        return settings.RABBITMQ_EXCHANGE
    except Exception as exc:  # noqa: BLE001
        log.warning("events: publish failed (%s)", exc)
        return None
    finally:
        try:
            await connection.close()
        except Exception:  # noqa: BLE001
            pass


__all__ = ["publish_sync_event", "sync_lock"]
