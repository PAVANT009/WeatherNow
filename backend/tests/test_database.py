"""Database model and schema integration tests.

These tests require a running PostgreSQL instance configured via DATABASE_URL.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.seed import seed_bengaluru
from app.db.seed_data import BENGALURU_SEED
from app.db.session import SessionLocal, engine
from app.models import City, District, WeatherRecord


def _database_available() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _database_available(),
    reason="PostgreSQL is not available (start docker compose first)",
)


@pytest.fixture()
def db() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _delete_weather_at(db: Session, district_id: int, observed_at: datetime) -> None:
    """Remove leftover test rows so fixed timestamps stay idempotent."""
    existing = db.scalars(
        select(WeatherRecord).where(
            WeatherRecord.district_id == district_id,
            WeatherRecord.observed_at == observed_at,
        )
    ).all()
    for row in existing:
        db.delete(row)
    if existing:
        db.commit()


def test_expected_tables_exist() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    assert {"cities", "districts", "weather_records", "alembic_version"} <= table_names


def test_seed_bengaluru_creates_districts(db: Session) -> None:
    city = seed_bengaluru(db)
    assert city.name == "Bengaluru"
    assert city.country_code == "IN"
    assert len(city.districts) == len(BENGALURU_SEED["districts"])

    district_names = {district.name for district in city.districts}
    expected_names = {item["name"] for item in BENGALURU_SEED["districts"]}
    assert district_names == expected_names

    # Idempotent seed: second call should not create duplicate records
    again = seed_bengaluru(db)
    assert again.id == city.id
    count = db.scalar(select(City).where(City.name == "Bengaluru"))
    assert count is not None


def test_city_district_relationship(db: Session) -> None:
    city = seed_bengaluru(db)
    district = city.districts[0]
    assert district.city.id == city.id
    assert district.city_id == city.id


def test_weather_record_links_to_district(db: Session) -> None:
    city = seed_bengaluru(db)
    district = city.districts[0]
    observed_at = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
    _delete_weather_at(db, district.id, observed_at)

    record = WeatherRecord(
        district_id=district.id,
        temperature=Decimal("27.50"),
        feels_like=Decimal("28.10"),
        humidity=55,
        wind_speed=Decimal("12.30"),
        weather_status="Clear",
        weather_description="Clear sky",
        provider="test",
        observed_at=observed_at,
        fetched_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    assert record.id is not None
    assert record.district.name == district.name
    db.refresh(district)
    assert any(row.id == record.id for row in district.weather_records)


def test_duplicate_weather_observation_is_rejected(db: Session) -> None:
    city = seed_bengaluru(db)
    district = city.districts[0]
    observed_at = datetime(2026, 8, 3, 15, 0, tzinfo=timezone.utc)
    _delete_weather_at(db, district.id, observed_at)

    def make_record() -> WeatherRecord:
        return WeatherRecord(
            district_id=district.id,
            temperature=Decimal("24.00"),
            feels_like=None,
            humidity=60,
            wind_speed=Decimal("8.00"),
            weather_status="Clouds",
            weather_description=None,
            provider="test",
            observed_at=observed_at,
            fetched_at=datetime.now(timezone.utc),
        )

    db.add(make_record())
    db.commit()

    db.add(make_record())
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_cannot_delete_city_with_districts(db: Session) -> None:
    city = seed_bengaluru(db)
    db.delete(city)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_indexes_exist() -> None:
    inspector = inspect(engine)
    district_indexes = {index["name"] for index in inspector.get_indexes("districts")}
    weather_indexes = {
        index["name"] for index in inspector.get_indexes("weather_records")
    }

    assert "ix_districts_city_id" in district_indexes
    assert "ix_weather_records_district_id" in weather_indexes
    assert "ix_weather_records_observed_at" in weather_indexes
    assert "ix_weather_records_district_id_observed_at" in weather_indexes
