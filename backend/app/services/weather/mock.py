"""Deterministic mock weather provider for tests."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.services.weather.base import (
    WeatherObservation,
    WeatherProvider,
    WeatherProviderError,
)
from app.services.weather.codes import describe_weather_code


class MockWeatherProvider(WeatherProvider):
    """Returns canned observations or raises a configured error."""

    def __init__(
        self,
        *,
        observation: WeatherObservation | None = None,
        error: WeatherProviderError | None = None,
    ) -> None:
        self._observation = observation
        self._error = error

    def fetch_current(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
    ) -> WeatherObservation:
        if self._error is not None:
            raise self._error

        if self._observation is not None:
            return self._observation

        status, description = describe_weather_code(0)
        # Latitude is folded into temperature so tests can distinguish districts.
        temperature = Decimal("20.00") + (latitude % Decimal("5"))
        return WeatherObservation(
            temperature=temperature.quantize(Decimal("0.01")),
            feels_like=temperature.quantize(Decimal("0.01")),
            humidity=55,
            wind_speed=Decimal("10.00"),
            weather_code=0,
            weather_status=status,
            weather_description=description,
            observed_at=datetime.now(timezone.utc).replace(second=0, microsecond=0),
            provider="mock",
        )
