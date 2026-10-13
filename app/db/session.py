"""SQLAlchemy engine and non-blocking database readiness checks."""

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, text

from app.core.config import DatabaseSettings


@dataclass(frozen=True)
class DatabaseHealth:
    connected: bool
    table_count: int | None


class DatabaseManager:
    """Own an engine and expose a safe connectivity check."""

    def __init__(self, engine: Any) -> None:
        self._engine = engine

    @classmethod
    def from_settings(cls, settings: DatabaseSettings) -> "DatabaseManager":
        engine = create_engine(
            settings.url,
            pool_size=settings.pool_size,
            pool_pre_ping=True,
        )
        return cls(engine)

    @classmethod
    def from_engine(cls, engine: Any) -> "DatabaseManager":
        return cls(engine)

    async def health(self) -> DatabaseHealth:
        return await asyncio.to_thread(self._health_sync)

    def _health_sync(self) -> DatabaseHealth:
        query = text(
            "SELECT count(*) "
            "FROM information_schema.tables "
            "WHERE table_schema = 'rag' AND table_type = 'BASE TABLE'"
        )
        with self._engine.connect() as connection:
            result = connection.execute(query)
            count = result.scalar_one()
        return DatabaseHealth(connected=True, table_count=int(count))

    async def close(self) -> None:
        await asyncio.to_thread(self._engine.dispose)
