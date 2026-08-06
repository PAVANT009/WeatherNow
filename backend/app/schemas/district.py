"""Pydantic schemas for district create/read operations."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DistrictCreate(BaseModel):
    """Request body for creating a district under an existing city."""

    city_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=120)
    latitude: Decimal
    longitude: Decimal

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be empty")
        return cleaned

    @field_validator("latitude")
    @classmethod
    def latitude_range(cls, value: Decimal) -> Decimal:
        if value < Decimal("-90") or value > Decimal("90"):
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude")
    @classmethod
    def longitude_range(cls, value: Decimal) -> Decimal:
        if value < Decimal("-180") or value > Decimal("180"):
            raise ValueError("longitude must be between -180 and 180")
        return value


class DistrictRead(BaseModel):
    """District resource returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    city_id: int
    name: str
    latitude: Decimal
    longitude: Decimal
    created_at: datetime
