from fastapi.testclient import TestClient

from app.core.config import DatabaseSettings, Settings
from app.db.session import DatabaseHealth, DatabaseManager
from app.main import create_app


class FakeDatabaseManager(DatabaseManager):
    def __init__(self) -> None:
        pass

    async def health(self) -> DatabaseHealth:
        return DatabaseHealth(connected=True, table_count=3)

    async def close(self) -> None:
        return None


def _test_settings() -> Settings:
    return Settings(
        environment="test",
        database=DatabaseSettings(url="postgresql+psycopg://test:test@localhost/test"),
    )


def test_application_startup_and_health_routes() -> None:
    client = TestClient(create_app(_test_settings(), FakeDatabaseManager()))

    with client:
        health = client.get("/health")
        ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["checks"]["database"] == "connected"
    assert ready.json()["table_count"] == 3
    assert health.headers["X-Request-ID"]
    assert ready.headers["X-Request-ID"]


def test_unknown_route_uses_safe_error_envelope() -> None:
    with TestClient(create_app(_test_settings(), FakeDatabaseManager())) as client:
        response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["X-Request-ID"]
