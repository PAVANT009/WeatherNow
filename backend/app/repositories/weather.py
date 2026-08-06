"""Weather record data-access helpers."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import WeatherRecord
from app.services.weather.base import WeatherObservation


def get_by_district_and_observed_at(
    db: Session,
    district_id: int,
    observed_at: datetime,
) -> WeatherRecord | None:
    """Return an existing observation for the unique (district, time) pair."""
    return db.scalar(
        select(WeatherRecord).where(
            WeatherRecord.district_id == district_id,
            WeatherRecord.observed_at == observed_at,
        )
    )


def create_weather_record(
    db: Session,
    *,
    district_id: int,
    observation: WeatherObservation,
    fetched_at: datetime,
) -> WeatherRecord | None:
    """Insert a weather row.

    Returns the created row, or ``None`` when the unique constraint means the
    same district/observed_at pair was already stored.
    """
    existing = get_by_district_and_observed_at(db, district_id, observation.observed_at)
    if existing is not None:
        return None

    record = WeatherRecord(
        district_id=district_id,
        temperature=observation.temperature,
        feels_like=observation.feels_like,
        humidity=observation.humidity,
        wind_speed=observation.wind_speed,
        weather_status=observation.weather_status,
        weather_description=observation.weather_description,
        provider=observation.provider,
        observed_at=observation.observed_at,
        fetched_at=fetched_at,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None

    db.refresh(record)
    return record
