from typing import Any

import pytest

from app.db.session import DatabaseHealth, DatabaseManager


class FakeConnection:
    def __enter__(self) -> "FakeConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, _query: Any) -> Any:
        return FakeResult()


class FakeResult:
    def scalar_one(self) -> int:
        return 7


class FakeEngine:
    def connect(self) -> FakeConnection:
        return FakeConnection()

    def dispose(self) -> None:
        return None


@pytest.mark.asyncio
async def test_database_manager_reports_table_count() -> None:
    manager = DatabaseManager.from_engine(FakeEngine())

    health = await manager.health()

    assert health == DatabaseHealth(connected=True, table_count=7)
