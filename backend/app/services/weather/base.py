"""Weather provider abstraction shared by real and mock implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class WeatherObservation(BaseModel):
    """Normalized weather snapshot produced by any provider."""

    temperature: Decimal = Field(..., ge=Decimal("-90"), le=Decimal("60"))
    feels_like: Decimal | None = Field(default=None, ge=Decimal("-90"), le=Decimal("60"))
    humidity: int = Field(..., ge=0, le=100)
    wind_speed: Decimal = Field(..., ge=Decimal("0"))
    weather_code: int
    weather_status: str
    weather_description: str | None = None
    observed_at: datetime
    provider: str

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        """Reject naive timestamps so comparisons stay unambiguous."""
        if value.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")
        return value


class WeatherProviderError(Exception):
    """Raised when a weather provider cannot return a valid observation."""

    def __init__(self, message: str, *, code: str = "WEATHER_PROVIDER_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class WeatherProvider(ABC):
    """Interface for external weather data sources."""

    @abstractmethod
    def fetch_current(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
    ) -> WeatherObservation:
        """Fetch the current weather for a coordinate pair."""
