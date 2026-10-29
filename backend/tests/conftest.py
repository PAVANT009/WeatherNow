"""Shared pytest fixtures for API tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.seed import seed_all_indian_cities, seed_bengaluru
from app.db.session import SessionLocal, engine
from app.main import app


def _database_available() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def database_ready() -> None:
    if not _database_available():
        pytest.skip("PostgreSQL is not available (start docker compose first)")


@pytest.fixture()
def api_client() -> Generator[TestClient, None, None]:
    """HTTP client that does not require PostgreSQL (pure JSON endpoints)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def client(database_ready: None) -> Generator[TestClient, None, None]:
    """HTTP client against the real app + PostgreSQL."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def seeded_city(database_ready: None) -> dict[str, int]:
    """Ensure Indian cities seed exists; return Bengaluru city id and first locality id."""
    db = SessionLocal()
    try:
        city = seed_bengaluru(db)
        district_id = city.districts[0].id
        return {"city_id": city.id, "district_id": district_id}
    finally:
        db.close()


@pytest.fixture()
def seeded_canakkale(seeded_city: dict[str, int]) -> dict[str, int]:
    """Backward-compatible fixture alias."""
    return seeded_city
