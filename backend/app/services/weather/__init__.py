"""Factory for the configured weather provider implementation."""

from __future__ import annotations

from app.core.config import get_settings
from app.services.weather.base import WeatherProvider
from app.services.weather.mock import MockWeatherProvider
from app.services.weather.open_meteo import OpenMeteoWeatherProvider


def get_weather_provider() -> WeatherProvider:
    """Build the provider selected by ``WEATHER_PROVIDER``."""
    settings = get_settings()
    name = settings.weather_provider.lower().strip()

    if name == "mock":
        return MockWeatherProvider()

    return OpenMeteoWeatherProvider(
        base_url=settings.weather_provider_base_url,
        timeout_seconds=settings.weather_provider_timeout_seconds,
    )
