"""Weather fetch and analysis routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_weather_provider_dep
from app.schemas.weather import (
    CompareResponse,
    CurrentWeatherItem,
    WeatherFetchResult,
    WeatherRecordRead,
    WeatherSummaryResponse,
)
from app.services import weather_analysis as analysis_service
from app.services import weather_fetch as weather_fetch_service
from app.services.weather.base import WeatherProvider

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/current", response_model=list[CurrentWeatherItem])
def current_for_city(
    city_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
) -> list[CurrentWeatherItem]:
    """Return the latest stored weather for every district in a city."""
    return analysis_service.get_current_for_city(db, city_id)


@router.get("/current/{district_id}", response_model=CurrentWeatherItem)
def current_for_district(
    district_id: int,
    db: Session = Depends(get_db),
) -> CurrentWeatherItem:
    """Return the latest stored weather for one district."""
    return analysis_service.get_current_for_district(db, district_id)


@router.get("/history/{district_id}", response_model=list[WeatherRecordRead])
def weather_history(
    district_id: int,
    start_date: datetime = Query(..., description="Timezone-aware start datetime"),
    end_date: datetime = Query(..., description="Timezone-aware end datetime"),
    db: Session = Depends(get_db),
) -> list[WeatherRecordRead]:
    """Return weather history for a district inside a date range."""
    return analysis_service.get_history(db, district_id, start_date, end_date)


@router.get("/compare", response_model=CompareResponse)
def compare_weather(
    district_ids: str = Query(
        ...,
        description="Comma-separated district ids, e.g. 1,2,3",
        examples=["1,2,3"],
    ),
    metric: str = Query(
        ...,
        description="One of: temperature, humidity, wind_speed",
        examples=["temperature"],
    ),
    db: Session = Depends(get_db),
) -> CompareResponse:
    """Compare selected districts on a single metric using latest records."""
    parsed_ids = _parse_district_ids(district_ids)
    return analysis_service.compare_districts(db, parsed_ids, metric)


@router.get("/summary", response_model=WeatherSummaryResponse)
def weather_summary(
    city_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
) -> WeatherSummaryResponse:
    """Return hottest/coldest/humid/windy extremes and averages for a city."""
    return analysis_service.get_city_summary(db, city_id)


# More specific ``/fetch/district/...`` must be registered before ``/fetch/{city_id}``.
@router.post("/fetch/district/{district_id}", response_model=WeatherFetchResult)
def fetch_district_weather(
    district_id: int,
    db: Session = Depends(get_db),
    provider: WeatherProvider = Depends(get_weather_provider_dep),
) -> WeatherFetchResult:
    """Fetch current weather for a single district and persist the result."""
    return weather_fetch_service.fetch_for_district(db, district_id, provider)


@router.post("/fetch/{city_id}", response_model=WeatherFetchResult)
def fetch_city_weather(
    city_id: int,
    db: Session = Depends(get_db),
    provider: WeatherProvider = Depends(get_weather_provider_dep),
) -> WeatherFetchResult:
    """Fetch current weather for all districts in a city and persist results."""
    return weather_fetch_service.fetch_for_city(db, city_id, provider)


def _parse_district_ids(raw: str) -> list[int]:
    parts = [part.strip() for part in raw.split(",") if part.strip()]
    if not parts:
        from app.core.exceptions import AppError

        raise AppError(
            code="INVALID_DISTRICT_SELECTION",
            message="district_ids must contain at least one id",
            status_code=422,
        )
    try:
        return [int(part) for part in parts]
    except ValueError as exc:
        from app.core.exceptions import AppError

        raise AppError(
            code="INVALID_DISTRICT_SELECTION",
            message="district_ids must be a comma-separated list of integers",
            status_code=422,
        ) from exc
