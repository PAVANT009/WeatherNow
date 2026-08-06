"""ORM models for cities, districts, and weather records."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class City(Base):
    """A city that owns one or more districts."""

    __tablename__ = "cities"
    __table_args__ = (
        UniqueConstraint("name", "country_code", name="uq_cities_name_country_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="TR")
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # RESTRICT: şehir silinince ilçeler otomatik silinmez; önce ilçeler temizlenmeli.
    districts: Mapped[list["District"]] = relationship(
        back_populates="city",
        cascade="save-update",
        passive_deletes=True,
    )


class District(Base):
    """A district belonging to a city, with map coordinates for weather lookup."""

    __tablename__ = "districts"
    __table_args__ = (
        UniqueConstraint("city_id", "name", name="uq_districts_city_id_name"),
        Index("ix_districts_city_id", "city_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    city: Mapped["City"] = relationship(back_populates="districts")
    # RESTRICT: ilçe silinince geçmiş hava kayıtları otomatik silinmez.
    weather_records: Mapped[list["WeatherRecord"]] = relationship(
        back_populates="district",
        cascade="save-update",
        passive_deletes=True,
    )


class WeatherRecord(Base):
    """A single weather observation for a district at a point in time."""

    __tablename__ = "weather_records"
    __table_args__ = (
        UniqueConstraint(
            "district_id",
            "observed_at",
            name="uq_weather_records_district_observed_at",
        ),
        Index("ix_weather_records_district_id", "district_id"),
        Index("ix_weather_records_observed_at", "observed_at"),
        Index(
            "ix_weather_records_district_id_observed_at",
            "district_id",
            "observed_at",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    district_id: Mapped[int] = mapped_column(
        ForeignKey("districts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    temperature: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    feels_like: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    wind_speed: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    weather_status: Mapped[str] = mapped_column(String(80), nullable=False)
    weather_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    district: Mapped["District"] = relationship(back_populates="weather_records")
