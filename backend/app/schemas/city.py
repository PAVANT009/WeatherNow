"""Pydantic schemas for city create/read operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_optional_latitude(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return value
    if value < Decimal("-90") or value > Decimal("90"):
        raise ValueError("latitude must be between -90 and 90")
    return value


def _validate_optional_longitude(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return value
    if value < Decimal("-180") or value > Decimal("180"):
        raise ValueError("longitude must be between -180 and 180")
    return value


class CityCreate(BaseModel):
    """Request body for creating a city."""

    name: str = Field(..., min_length=1, max_length=120)
    country_code: str = Field(default="TR", min_length=2, max_length=2)
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be empty")
        return cleaned

    @field_validator("country_code")
    @classmethod
    def country_code_upper(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("latitude")
    @classmethod
    def latitude_range(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_optional_latitude(value)

    @field_validator("longitude")
    @classmethod
    def longitude_range(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        return _validate_optional_longitude(value)


class CityRead(BaseModel):
    """City resource returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country_code: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    created_at: datetime
