"""Weather analysis orchestration (current, history, compare, summary)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.repositories import city as city_repository
from app.repositories import district as district_repository
from app.repositories import weather_analysis as analysis_repository
from app.schemas.weather import (
    CompareItem,
    CompareResponse,
    CurrentWeatherItem,
    ExtremeDistrict,
    WeatherRecordRead,
    WeatherSummaryResponse,
)

SUPPORTED_METRICS = frozenset({"temperature", "humidity", "wind_speed"})


def get_current_for_city(db: Session, city_id: int) -> list[CurrentWeatherItem]:
    """Return latest weather for every district that has records in the city."""
    _require_city(db, city_id)
    rows = analysis_repository.list_current_for_city(db, city_id)
    return [
        CurrentWeatherItem(
            district_id=row["district_id"],
            district_name=row["district_name"],
            temperature=row["record"].temperature,
            feels_like=row["record"].feels_like,
            humidity=row["record"].humidity,
            wind_speed=row["record"].wind_speed,
            weather_status=row["record"].weather_status,
            weather_description=row["record"].weather_description,
            provider=row["record"].provider,
            observed_at=row["record"].observed_at,
            fetched_at=row["record"].fetched_at,
        )
        for row in rows
    ]


def get_current_for_district(db: Session, district_id: int) -> CurrentWeatherItem:
    """Return the latest weather for one district."""
    district = district_repository.get_district_by_id(db, district_id)
    if district is None:
        raise AppError(
            code="DISTRICT_NOT_FOUND",
            message="District could not be found",
            status_code=404,
        )

    result = analysis_repository.get_current_for_district(db, district_id)
    if result is None:
        raise AppError(
            code="WEATHER_NOT_FOUND",
            message="No weather record found for this district",
            status_code=404,
        )

    record, district_row = result
    return CurrentWeatherItem(
        district_id=district_row.id,
        district_name=district_row.name,
        temperature=record.temperature,
        feels_like=record.feels_like,
        humidity=record.humidity,
        wind_speed=record.wind_speed,
        weather_status=record.weather_status,
        weather_description=record.weather_description,
        provider=record.provider,
        observed_at=record.observed_at,
        fetched_at=record.fetched_at,
    )


def get_history(
    db: Session,
    district_id: int,
    start_date: datetime,
    end_date: datetime,
) -> list[WeatherRecordRead]:
    """Return history for a district after validating the date window."""
    if start_date.tzinfo is None or end_date.tzinfo is None:
        raise AppError(
            code="INVALID_DATE_RANGE",
            message="start_date and end_date must include timezone information",
            status_code=422,
        )
    if start_date > end_date:
        raise AppError(
            code="INVALID_DATE_RANGE",
            message="start_date must be less than or equal to end_date",
            status_code=422,
        )

    district = district_repository.get_district_by_id(db, district_id)
    if district is None:
        raise AppError(
            code="DISTRICT_NOT_FOUND",
            message="District could not be found",
            status_code=404,
        )

    records = analysis_repository.list_history(db, district_id, start_date, end_date)
    return [WeatherRecordRead.model_validate(record) for record in records]


def compare_districts(
    db: Session,
    district_ids: list[int],
    metric: str,
) -> CompareResponse:
    """Compare latest metric values across 2–10 districts."""
    if metric not in SUPPORTED_METRICS:
        raise AppError(
            code="INVALID_METRIC",
            message="metric must be one of: temperature, humidity, wind_speed",
            status_code=422,
        )

    unique_ids = list(dict.fromkeys(district_ids))
    if len(unique_ids) < 2 or len(unique_ids) > 10:
        raise AppError(
            code="INVALID_DISTRICT_SELECTION",
            message="Select between 2 and 10 distinct districts",
            status_code=422,
        )

    for district_id in unique_ids:
        if district_repository.get_district_by_id(db, district_id) is None:
            raise AppError(
                code="DISTRICT_NOT_FOUND",
                message=f"District {district_id} could not be found",
                status_code=404,
            )

    rows = analysis_repository.compare_latest(db, unique_ids, metric)
    items = [
        CompareItem(
            district_id=row["district_id"],
            district_name=row["district_name"],
            metric=metric,  # type: ignore[arg-type]
            value=Decimal(str(row["value"])),
            observed_at=row["observed_at"],
        )
        for row in rows
    ]
    return CompareResponse(metric=metric, items=items)  # type: ignore[arg-type]


def get_city_summary(db: Session, city_id: int) -> WeatherSummaryResponse:
    """Return SQL-aggregate summary for a city's latest district weather."""
    _require_city(db, city_id)
    summary = analysis_repository.city_summary(db, city_id)
    if summary is None:
        raise AppError(
            code="WEATHER_NOT_FOUND",
            message="No weather records found for this city",
            status_code=404,
        )

    def _extreme(payload: dict) -> ExtremeDistrict:
        return ExtremeDistrict(
            district_id=payload["district_id"],
            district_name=payload["district_name"],
            value=Decimal(str(payload["value"])),
        )

    return WeatherSummaryResponse(
        city_id=city_id,
        district_count=summary["district_count"],
        average_temperature=Decimal(str(summary["average_temperature"])),
        average_humidity=Decimal(str(summary["average_humidity"])),
        last_updated_at=summary["last_updated_at"],
        hottest=_extreme(summary["hottest"]),
        coldest=_extreme(summary["coldest"]),
        most_humid=_extreme(summary["most_humid"]),
        windiest=_extreme(summary["windiest"]),
    )


def _require_city(db: Session, city_id: int) -> None:
    if city_repository.get_city_by_id(db, city_id) is None:
        raise AppError(
            code="CITY_NOT_FOUND",
            message="City could not be found",
            status_code=404,
        )
