"""SQL-backed weather analysis queries (current, history, compare, summary)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import District, WeatherRecord

METRIC_COLUMNS = {
    "temperature": WeatherRecord.temperature,
    "humidity": WeatherRecord.humidity,
    "wind_speed": WeatherRecord.wind_speed,
}


def _latest_per_district_subquery(city_id: int | None = None):
    """Subquery: district_id + max(observed_at), optionally scoped to a city."""
    stmt = select(
        WeatherRecord.district_id.label("district_id"),
        func.max(WeatherRecord.observed_at).label("max_observed_at"),
    ).join(District, District.id == WeatherRecord.district_id)

    if city_id is not None:
        stmt = stmt.where(District.city_id == city_id)

    return stmt.group_by(WeatherRecord.district_id).subquery()


def list_current_for_city(db: Session, city_id: int) -> list[dict[str, Any]]:
    """Return latest weather row + district fields for each district in a city."""
    latest = _latest_per_district_subquery(city_id)
    stmt = (
        select(WeatherRecord, District)
        .join(District, District.id == WeatherRecord.district_id)
        .join(
            latest,
            (WeatherRecord.district_id == latest.c.district_id)
            & (WeatherRecord.observed_at == latest.c.max_observed_at),
        )
        .where(District.city_id == city_id)
        .order_by(District.name, District.id)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "district_id": district.id,
            "district_name": district.name,
            "record": record,
        }
        for record, district in rows
    ]


def get_current_for_district(
    db: Session,
    district_id: int,
) -> tuple[WeatherRecord, District] | None:
    """Return the latest weather record for one district, or None."""
    stmt = (
        select(WeatherRecord, District)
        .join(District, District.id == WeatherRecord.district_id)
        .where(WeatherRecord.district_id == district_id)
        .order_by(WeatherRecord.observed_at.desc())
        .limit(1)
    )
    return db.execute(stmt).first()


def list_history(
    db: Session,
    district_id: int,
    start_date: datetime,
    end_date: datetime,
) -> list[WeatherRecord]:
    """Return weather history for a district inside an inclusive time window."""
    stmt = (
        select(WeatherRecord)
        .where(
            WeatherRecord.district_id == district_id,
            WeatherRecord.observed_at >= start_date,
            WeatherRecord.observed_at <= end_date,
        )
        .order_by(WeatherRecord.observed_at.asc())
    )
    return list(db.scalars(stmt).all())


def compare_latest(
    db: Session,
    district_ids: list[int],
    metric: str,
) -> list[dict[str, Any]]:
    """Compare districts on a metric using each district's latest observation."""
    column = METRIC_COLUMNS[metric]
    latest = (
        select(
            WeatherRecord.district_id.label("district_id"),
            func.max(WeatherRecord.observed_at).label("max_observed_at"),
        )
        .where(WeatherRecord.district_id.in_(district_ids))
        .group_by(WeatherRecord.district_id)
        .subquery()
    )

    stmt = (
        select(
            District.id,
            District.name,
            column.label("value"),
            WeatherRecord.observed_at,
        )
        .join(WeatherRecord, WeatherRecord.district_id == District.id)
        .join(
            latest,
            (WeatherRecord.district_id == latest.c.district_id)
            & (WeatherRecord.observed_at == latest.c.max_observed_at),
        )
        .where(District.id.in_(district_ids))
        .order_by(District.name, District.id)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "district_id": row.id,
            "district_name": row.name,
            "metric": metric,
            "value": row.value,
            "observed_at": row.observed_at,
        }
        for row in rows
    ]


def city_summary(db: Session, city_id: int) -> dict[str, Any] | None:
    """Aggregate latest-per-district stats for a city using SQL aggregates."""
    latest = _latest_per_district_subquery(city_id)

    latest_rows = (
        select(
            WeatherRecord.district_id.label("district_id"),
            District.name.label("district_name"),
            WeatherRecord.temperature.label("temperature"),
            WeatherRecord.humidity.label("humidity"),
            WeatherRecord.wind_speed.label("wind_speed"),
            WeatherRecord.fetched_at.label("fetched_at"),
            WeatherRecord.observed_at.label("observed_at"),
        )
        .join(District, District.id == WeatherRecord.district_id)
        .join(
            latest,
            (WeatherRecord.district_id == latest.c.district_id)
            & (WeatherRecord.observed_at == latest.c.max_observed_at),
        )
        .where(District.city_id == city_id)
        .subquery()
    )

    aggregates = db.execute(
        select(
            func.count().label("district_count"),
            func.avg(latest_rows.c.temperature).label("avg_temperature"),
            func.avg(latest_rows.c.humidity).label("avg_humidity"),
            func.max(latest_rows.c.fetched_at).label("last_updated_at"),
            func.max(latest_rows.c.temperature).label("max_temperature"),
            func.min(latest_rows.c.temperature).label("min_temperature"),
            func.max(latest_rows.c.humidity).label("max_humidity"),
            func.max(latest_rows.c.wind_speed).label("max_wind_speed"),
        )
    ).one()

    if not aggregates.district_count:
        return None

    def _extreme(column_name: str, extreme_value: Decimal | float | int) -> dict[str, Any]:
        column = getattr(latest_rows.c, column_name)
        row = db.execute(
            select(
                latest_rows.c.district_id,
                latest_rows.c.district_name,
                column.label("value"),
            )
            .where(column == extreme_value)
            .order_by(latest_rows.c.district_name)
            .limit(1)
        ).one()
        return {
            "district_id": row.district_id,
            "district_name": row.district_name,
            "value": row.value,
        }

    return {
        "city_id": city_id,
        "district_count": aggregates.district_count,
        "average_temperature": aggregates.avg_temperature,
        "average_humidity": aggregates.avg_humidity,
        "last_updated_at": aggregates.last_updated_at,
        "hottest": _extreme("temperature", aggregates.max_temperature),
        "coldest": _extreme("temperature", aggregates.min_temperature),
        "most_humid": _extreme("humidity", aggregates.max_humidity),
        "windiest": _extreme("wind_speed", aggregates.max_wind_speed),
    }
