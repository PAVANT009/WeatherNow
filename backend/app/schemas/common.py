"""Shared response schemas used across API modules."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Nested error body under FastAPI's ``detail`` key."""

    code: str = Field(..., examples=["CITY_NOT_FOUND"])
    message: str = Field(..., examples=["City could not be found"])


class HealthResponse(BaseModel):
    """Health check payload for probes and Swagger demos."""

    status: str = Field(..., examples=["ok"])
    database: str = Field(..., examples=["connected"])
