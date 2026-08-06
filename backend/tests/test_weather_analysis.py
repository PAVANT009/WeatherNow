"""Tests for weather analysis endpoints (current, history, compare, summary)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import WeatherRecord


def _insert_record(
    *,
    district_id: int,
    temperature: str,
    humidity: int,
    wind_speed: str,
    observed_at: datetime,
) -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(
            select(WeatherRecord).where(
                WeatherRecord.district_id == district_id,
                WeatherRecord.observed_at == observed_at,
            )
        )
        if existing is not None:
            db.delete(existing)
            db.commit()

        db.add(
            WeatherRecord(
                district_id=district_id,
                temperature=Decimal(temperature),
                feels_like=Decimal(temperature),
                humidity=humidity,
                wind_speed=Decimal(wind_speed),
                weather_status="Açık",
                weather_description="test",
                provider="test",
                observed_at=observed_at,
                fetched_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
    finally:
        db.close()


def _cleanup_provider(provider: str = "test") -> None:
    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(WeatherRecord).where(WeatherRecord.provider == provider)
            ).all()
        )
        for row in rows:
            db.delete(row)
        db.commit()
    finally:
        db.close()


def _cleanup_city_weather(city_id: int) -> None:
    """Remove all weather rows for districts in a city (stable summary tests)."""
    db = SessionLocal()
    try:
        from app.models import District

        district_ids = list(
            db.scalars(select(District.id).where(District.city_id == city_id)).all()
        )
        if not district_ids:
            return
        rows = list(
            db.scalars(
                select(WeatherRecord).where(
                    WeatherRecord.district_id.in_(district_ids)
                )
            ).all()
        )
        for row in rows:
            db.delete(row)
        db.commit()
    finally:
        db.close()


def test_invalid_date_range_returns_422(
    client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    district_id = seeded_canakkale["district_id"]
    start = "2026-08-10T00:00:00+00:00"
    end = "2026-08-01T00:00:00+00:00"
    response = client.get(
        f"/api/v1/weather/history/{district_id}",
        params={"start_date": start, "end_date": end},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_DATE_RANGE"


def test_compare_invalid_metric_returns_422(
    client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    db = SessionLocal()
    try:
        from app.models import District

        districts = list(
            db.scalars(
                select(District).where(
                    District.city_id == seeded_canakkale["city_id"]
                )
            ).all()
        )
        ids = f"{districts[0].id},{districts[1].id}"
    finally:
        db.close()

    response = client.get(
        "/api/v1/weather/compare",
        params={"district_ids": ids, "metric": "pressure"},
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_METRIC"


def test_summary_and_current(
    client: TestClient,
    seeded_canakkale: dict[str, int],
) -> None:
    city_id = seeded_canakkale["city_id"]
    _cleanup_city_weather(city_id)

    db = SessionLocal()
    try:
        from app.models import District

        districts = list(
            db.scalars(
                select(District)
                .where(District.city_id == city_id)
                .order_by(District.name)
            ).all()
        )
    finally:
        db.close()

    assert len(districts) >= 3
    base = datetime.now(timezone.utc).replace(microsecond=0)

    # Hottest / coldest / humid / windy extremes are deterministic.
    _insert_record(
        district_id=districts[0].id,
        temperature="30.00",
        humidity=40,
        wind_speed="5.00",
        observed_at=base,
    )
    _insert_record(
        district_id=districts[1].id,
        temperature="10.00",
        humidity=90,
        wind_speed="3.00",
        observed_at=base + timedelta(minutes=1),
    )
    _insert_record(
        district_id=districts[2].id,
        temperature="20.00",
        humidity=50,
        wind_speed="25.00",
        observed_at=base + timedelta(minutes=2),
    )

    current = client.get("/api/v1/weather/current", params={"city_id": city_id})
    assert current.status_code == 200
    assert len(current.json()) >= 3

    one = client.get(f"/api/v1/weather/current/{districts[0].id}")
    assert one.status_code == 200
    assert Decimal(one.json()["temperature"]) == Decimal("30.00")

    summary = client.get("/api/v1/weather/summary", params={"city_id": city_id})
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["hottest"]["district_id"] == districts[0].id
    assert payload["coldest"]["district_id"] == districts[1].id
    assert payload["most_humid"]["district_id"] == districts[1].id
    assert payload["windiest"]["district_id"] == districts[2].id
    assert Decimal(payload["average_temperature"]) == Decimal("20")

    compare = client.get(
        "/api/v1/weather/compare",
        params={
            "district_ids": f"{districts[0].id},{districts[1].id}",
            "metric": "temperature",
        },
    )
    assert compare.status_code == 200
    assert compare.json()["metric"] == "temperature"
    assert len(compare.json()["items"]) == 2

    history = client.get(
        f"/api/v1/weather/history/{districts[0].id}",
        params={
            "start_date": (base - timedelta(hours=1)).isoformat(),
            "end_date": (base + timedelta(hours=1)).isoformat(),
        },
    )
    assert history.status_code == 200
    assert len(history.json()) >= 1

    _cleanup_city_weather(city_id)


def test_current_city_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/weather/current", params={"city_id": 999999})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "CITY_NOT_FOUND"
