"""Orchestrate weather fetch for cities and districts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import District
from app.repositories import city as city_repository
from app.repositories import district as district_repository
from app.repositories import weather as weather_repository
from app.schemas.weather import FetchDistrictError, WeatherFetchResult, WeatherRecordRead
from app.services.weather.base import WeatherProvider, WeatherProviderError


def fetch_for_city(
    db: Session,
    city_id: int,
    provider: WeatherProvider,
) -> WeatherFetchResult:
    """Fetch and persist current weather for every district in a city.

    One district failure does not abort the whole city batch.
    """
    city = city_repository.get_city_by_id(db, city_id)
    if city is None:
        raise AppError(
            code="CITY_NOT_FOUND",
            message="City could not be found",
            status_code=404,
        )

    districts = district_repository.list_districts_for_city(db, city_id)
    if not districts:
        raise AppError(
            code="CITY_HAS_NO_DISTRICTS",
            message="City has no districts to fetch weather for",
            status_code=400,
        )

    return _fetch_many(db, districts, provider)


def fetch_for_district(
    db: Session,
    district_id: int,
    provider: WeatherProvider,
) -> WeatherFetchResult:
    """Fetch and persist current weather for a single district."""
    district = district_repository.get_district_by_id(db, district_id)
    if district is None:
        raise AppError(
            code="DISTRICT_NOT_FOUND",
            message="District could not be found",
            status_code=404,
        )
    return _fetch_many(db, [district], provider)


def _fetch_many(
    db: Session,
    districts: list[District],
    provider: WeatherProvider,
) -> WeatherFetchResult:
    successful = 0
    failed = 0
    skipped = 0
    errors: list[FetchDistrictError] = []
    records: list[WeatherRecordRead] = []
    fetched_at = datetime.now(timezone.utc)

    for district in districts:
        try:
            observation = provider.fetch_current(
                latitude=district.latitude,
                longitude=district.longitude,
            )
            record = weather_repository.create_weather_record(
                db,
                district_id=district.id,
                observation=observation,
                fetched_at=fetched_at,
            )
            if record is None:
                skipped += 1
                continue
            successful += 1
            records.append(WeatherRecordRead.model_validate(record))
        except WeatherProviderError as exc:
            failed += 1
            errors.append(
                FetchDistrictError(district_id=district.id, message=exc.message)
            )

    return WeatherFetchResult(
        successful=successful,
        failed=failed,
        skipped_duplicates=skipped,
        errors=errors,
        records=records,
    )
