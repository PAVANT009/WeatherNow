"""Open-Meteo HTTP weather provider (no API key required)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.services.weather.base import (
    WeatherObservation,
    WeatherProvider,
    WeatherProviderError,
)
from app.services.weather.codes import describe_weather_code


class OpenMeteoCurrentBlock(BaseModel):
    """Subset of Open-Meteo ``current`` JSON fields we care about."""

    time: str
    temperature_2m: float
    relative_humidity_2m: int
    apparent_temperature: float | None = None
    weather_code: int
    wind_speed_10m: float


class OpenMeteoForecastResponse(BaseModel):
    """Minimal validation model for Open-Meteo forecast JSON."""

    current: OpenMeteoCurrentBlock
    utc_offset_seconds: int | None = None


class OpenMeteoWeatherProvider(WeatherProvider):
    """Calls the Open-Meteo Forecast API with a bounded timeout."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.open-meteo.com",
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._client = client

    def fetch_current(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
    ) -> WeatherObservation:
        params = {
            "latitude": str(latitude),
            "longitude": str(longitude),
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "weather_code,wind_speed_10m"
            ),
            "timezone": "UTC",
            "wind_speed_unit": "kmh",
        }
        url = f"{self._base_url}/v1/forecast"
        payload = self._request_json(url, params)
        return self._to_observation(payload)

    def _request_json(self, url: str, params: dict[str, str]) -> dict[str, Any]:
        owns_client = self._client is None
        client = self._client or httpx.Client(timeout=self._timeout)
        try:
            response = client.get(url, params=params)
        except httpx.TimeoutException as exc:
            raise WeatherProviderError(
                "Weather provider timeout",
                code="WEATHER_PROVIDER_TIMEOUT",
            ) from exc
        except httpx.RequestError as exc:
            raise WeatherProviderError(
                "Weather provider connection error",
                code="WEATHER_PROVIDER_CONNECTION",
            ) from exc
        finally:
            if owns_client:
                client.close()

        if response.status_code >= 500:
            raise WeatherProviderError(
                f"Weather provider server error ({response.status_code})",
                code="WEATHER_PROVIDER_SERVER_ERROR",
            )
        if response.status_code >= 400:
            raise WeatherProviderError(
                f"Weather provider client error ({response.status_code})",
                code="WEATHER_PROVIDER_CLIENT_ERROR",
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise WeatherProviderError(
                "Weather provider returned invalid JSON",
                code="WEATHER_PROVIDER_INVALID_JSON",
            ) from exc

        if not isinstance(data, dict):
            raise WeatherProviderError(
                "Weather provider returned unexpected JSON root",
                code="WEATHER_PROVIDER_UNEXPECTED_PAYLOAD",
            )
        return data

    def _to_observation(self, payload: dict[str, Any]) -> WeatherObservation:
        try:
            parsed = OpenMeteoForecastResponse.model_validate(payload)
        except ValidationError as exc:
            raise WeatherProviderError(
                "Weather provider returned incomplete or unexpected JSON",
                code="WEATHER_PROVIDER_UNEXPECTED_PAYLOAD",
            ) from exc

        status, description = describe_weather_code(parsed.current.weather_code)
        observed_at = self._parse_observed_at(parsed.current.time)

        return WeatherObservation(
            temperature=Decimal(str(parsed.current.temperature_2m)),
            feels_like=(
                Decimal(str(parsed.current.apparent_temperature))
                if parsed.current.apparent_temperature is not None
                else None
            ),
            humidity=parsed.current.relative_humidity_2m,
            wind_speed=Decimal(str(parsed.current.wind_speed_10m)),
            weather_code=parsed.current.weather_code,
            weather_status=status,
            weather_description=description,
            observed_at=observed_at,
            provider="open_meteo",
        )

    @staticmethod
    def _parse_observed_at(value: str) -> datetime:
        # Open-Meteo current.time examples: "2026-08-03T12:00" (UTC when timezone=UTC)
        normalized = value.replace("Z", "+00:00")
        if len(normalized) == 16:
            # YYYY-MM-DDTHH:MM → assume UTC
            normalized = f"{normalized}:00+00:00"
        elif "+" not in normalized[10:] and not normalized.endswith("+00:00"):
            normalized = f"{normalized}+00:00"
        try:
            return datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise WeatherProviderError(
                "Weather provider returned an invalid observation time",
                code="WEATHER_PROVIDER_UNEXPECTED_PAYLOAD",
            ) from exc
