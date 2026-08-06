"""Request/response schemas for weather fetch and analysis endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WeatherRecordRead(BaseModel):
    """API representation of a stored weather observation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    district_id: int
    temperature: Decimal
    feels_like: Decimal | None
    humidity: int
    wind_speed: Decimal
    weather_status: str
    weather_description: str | None
    provider: str
    observed_at: datetime
    fetched_at: datetime


class FetchDistrictError(BaseModel):
    """Per-district failure detail inside a batch fetch."""

    district_id: int
    message: str


class WeatherFetchResult(BaseModel):
    """Result of fetching weather for one or more districts."""

    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    skipped_duplicates: int = Field(0, ge=0)
    errors: list[FetchDistrictError] = Field(default_factory=list)
    records: list[WeatherRecordRead] = Field(default_factory=list)


class CurrentWeatherItem(BaseModel):
    """Latest weather for a district, including district identity."""

    district_id: int
    district_name: str
    temperature: Decimal
    feels_like: Decimal | None
    humidity: int
    wind_speed: Decimal
    weather_status: str
    weather_description: str | None
    provider: str
    observed_at: datetime
    fetched_at: datetime


class CompareItem(BaseModel):
    """One district's value in a metric comparison."""

    district_id: int
    district_name: str
    metric: Literal["temperature", "humidity", "wind_speed"]
    value: Decimal
    observed_at: datetime


class CompareResponse(BaseModel):
    """Comparison payload for selected districts and metric."""

    metric: Literal["temperature", "humidity", "wind_speed"]
    items: list[CompareItem]


class ExtremeDistrict(BaseModel):
    """District holding an extreme metric value in a city summary."""

    district_id: int
    district_name: str
    value: Decimal


class WeatherSummaryResponse(BaseModel):
    """Aggregated summary of the latest weather across a city's districts."""

    city_id: int
    district_count: int
    average_temperature: Decimal
    average_humidity: Decimal
    last_updated_at: datetime
    hottest: ExtremeDistrict
    coldest: ExtremeDistrict
    most_humid: ExtremeDistrict
    windiest: ExtremeDistrict
