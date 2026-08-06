"""Shared FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import get_db as _get_db
from app.services.weather import get_weather_provider
from app.services.weather.base import WeatherProvider


def get_db() -> Generator[Session, None, None]:
    """Provide a request-scoped SQLAlchemy session."""
    yield from _get_db()


def get_weather_provider_dep() -> WeatherProvider:
    """Resolve the configured weather provider (overridable in tests)."""
    return get_weather_provider()
