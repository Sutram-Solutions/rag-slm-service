"""Alembic environment.

Owns the `rag` schema only. The `app` schema belongs to Flyway on the Java
side; nothing here may touch it.
"""

import asyncio
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.settings import get_settings

# Windows defaults to ProactorEventLoop, which psycopg's async mode cannot use.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# One source of truth for the connection string.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

# No ORM models yet — autogenerate arrives with them in a later step.
target_metadata = None

RAG_SCHEMA = "rag"


def _configure(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table="alembic_version",
        version_table_schema=RAG_SCHEMA,  # version table lives in rag, not public
        include_schemas=True,
        compare_type=True,
        compare_server_default=True,
    )


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        version_table_schema=RAG_SCHEMA,
        include_schemas=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    _configure(connection)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
