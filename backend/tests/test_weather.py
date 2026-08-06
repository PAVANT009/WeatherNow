"""Weather provider and fetch endpoint tests (no real external API calls)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.dependencies import get_weather_provider_dep
from app.main import app
from app.models import WeatherRecord
from app.repositories import weather as weather_repository
from app.services.weather.base import WeatherObservation, WeatherProviderError
from app.services.weather.codes import describe_weather_code
from app.services.weather.mock import MockWeatherProvider
from app.services.weather.open_meteo import OpenMeteoWeatherProvider


def _fixed_observation(
    *,
    observed_at: datetime | None = None,
    temperature: str = "22.50",
) -> WeatherObservation:
    status, description = describe_weather_code(0)
    return WeatherObservation(
        temperature=Decimal(temperature),
        feels_like=Decimal("23.00"),
        humidity=50,
        wind_speed=Decimal("8.50"),
        weather_code=0,
        weather_status=status,
        weather_description=description,
        observed_at=observed_at
        or datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc),
        provider="mock",
    )


def _cleanup_observed_at(observed_at: datetime) -> None:
    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(WeatherRecord).where(WeatherRecord.observed_at == observed_at)
            ).all()
        )
        for row in rows:
            db.delete(row)
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def mock_provider_client(database_ready: None) -> TestClient:
    """TestClient with a successful mock weather provider injected."""
    provider = MockWeatherProvider(observation=_fixed_observation())

    def _override() -> MockWeatherProvider:
        return provider

    app.dependency_overrides[get_weather_provider_dep] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_weather_provider_dep, None)


def test_describe_weather_code_known() -> None:
    status, description = describe_weather_code(61)
    assert status == "Yağmurlu"
    assert "yağmur" in description.lower()


def test_open_meteo_provider_success_parses_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "current": {
                    "time": "2026-08-03T12:00",
                    "temperature_2m": 27.4,
                    "relative_humidity_2m": 48,
                    "apparent_temperature": 28.1,
                    "weather_code": 2,
                    "wind_speed_10m": 14.2,
                }
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, timeout=5.0) as client:
        provider = OpenMeteoWeatherProvider(
            base_url="https://example.test",
            client=client,
        )
        observation = provider.fetch_current(
            latitude=Decimal("40.1553000"),
            longitude=Decimal("26.4142000"),
        )

    assert observation.temperature == Decimal("27.4")
    assert observation.humidity == 48
    assert observation.weather_status == "Parçalı bulutlu"
    assert observation.observed_at.tzinfo is not None
    assert observation.provider == "open_meteo"


def test_open_meteo_provider_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, timeout=0.1) as client:
        provider = OpenMeteoWeatherProvider(
            base_url="https://example.test",
            client=client,
        )
        with pytest.raises(WeatherProviderError) as exc_info:
            provider.fetch_current(
                latitude=Decimal("40.0"),
                longitude=Decimal("26.0"),
            )
    assert exc_info.value.code == "WEATHER_PROVIDER_TIMEOUT"


def test_insert_weather_record_and_skip_duplicate(
    client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    district_id = seeded_canakkale["district_id"]
    observed_at = datetime(2026, 8, 3, 18, 30, tzinfo=timezone.utc)
    observation = _fixed_observation(observed_at=observed_at)
    fetched_at = datetime.now(timezone.utc)

    db = SessionLocal()
    try:
        existing = weather_repository.get_by_district_and_observed_at(
            db, district_id, observed_at
        )
        if existing is not None:
            db.delete(existing)
            db.commit()

        first = weather_repository.create_weather_record(
            db,
            district_id=district_id,
            observation=observation,
            fetched_at=fetched_at,
        )
        assert first is not None
        assert first.id is not None

        second = weather_repository.create_weather_record(
            db,
            district_id=district_id,
            observation=observation,
            fetched_at=fetched_at,
        )
        assert second is None
    finally:
        row = weather_repository.get_by_district_and_observed_at(
            db, district_id, observed_at
        )
        if row is not None:
            db.delete(row)
            db.commit()
        db.close()


def test_fetch_city_uses_mock_provider(
    mock_provider_client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    city_id = seeded_canakkale["city_id"]
    observed_at = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
    _cleanup_observed_at(observed_at)

    response = mock_provider_client.post(f"/api/v1/weather/fetch/{city_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["successful"] >= 1
    assert payload["failed"] == 0
    assert len(payload["records"]) == payload["successful"]

    _cleanup_observed_at(observed_at)


def test_fetch_city_partial_failure(
    client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    """Some districts succeed while others fail; city batch continues."""
    observed_at = datetime(2026, 8, 3, 13, 0, tzinfo=timezone.utc)
    _cleanup_observed_at(observed_at)

    class SelectiveProvider(MockWeatherProvider):
        def __init__(self) -> None:
            super().__init__(
                observation=_fixed_observation(observed_at=observed_at),
            )
            self._calls = 0

        def fetch_current(self, *, latitude: Decimal, longitude: Decimal):
            self._calls += 1
            if self._calls == 1:
                raise WeatherProviderError(
                    "Weather provider timeout",
                    code="WEATHER_PROVIDER_TIMEOUT",
                )
            return super().fetch_current(latitude=latitude, longitude=longitude)

    provider = SelectiveProvider()
    app.dependency_overrides[get_weather_provider_dep] = lambda: provider
    try:
        response = client.post(
            f"/api/v1/weather/fetch/{seeded_canakkale['city_id']}"
        )
    finally:
        app.dependency_overrides.pop(get_weather_provider_dep, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["failed"] == 1
    assert payload["successful"] >= 1
    assert payload["errors"][0]["message"] == "Weather provider timeout"

    _cleanup_observed_at(observed_at)


def test_fetch_unknown_city_returns_404(mock_provider_client: TestClient) -> None:
    response = mock_provider_client.post("/api/v1/weather/fetch/999999")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "CITY_NOT_FOUND"


def test_fetch_unknown_district_returns_404(mock_provider_client: TestClient) -> None:
    response = mock_provider_client.post("/api/v1/weather/fetch/district/999999")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "DISTRICT_NOT_FOUND"
