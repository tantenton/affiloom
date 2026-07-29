"""Alembic environment.

Runs migrations with a *sync* engine derived from the async URL so we don't
need to spin up an event loop inside the migration process. ``asyncpg`` -->
``psycopg``, ``aiosqlite`` --> ``sqlite`` handles the conversion; the app
itself continues to use the async drivers.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make ``apps/backend`` importable when Alembic is invoked from that dir.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from config import settings  # noqa: E402
from db.models import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _sync_url(url: str) -> str:
    if url.startswith("postgresql+asyncpg://"):
        return "postgresql+psycopg2://" + url[len("postgresql+asyncpg://") :]
    if url.startswith("sqlite+aiosqlite://"):
        return "sqlite://" + url[len("sqlite+aiosqlite://") :]
    return url


url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", _sync_url(url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
