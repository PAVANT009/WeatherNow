"""Pydantic schemas for educational / training exercise endpoints."""

from pydantic import BaseModel, Field


class NumberListRequest(BaseModel):
    """A JSON body carrying a list of numbers for exercise endpoints."""

    values: list[float] = Field(
        ...,
        min_length=1,
        description="Numeric array (JSON array). Example: [12, 18, 21, 24, 27, 29, 31, 33]",
        examples=[[12, 18, 21, 24, 27, 29, 31, 33]],
    )


class SeventhElementRequest(BaseModel):
    """Request for the '7th element' algorithm exercise."""

    values: list[float] = Field(
        ...,
        min_length=7,
        description=(
            "Number list with at least 7 items. "
            "In Python lists, 0-based indexing means the 7th element is at index 6."
        ),
        examples=[[12, 18, 21, 24, 27, 29, 31, 33]],
    )


class SeventhElementResponse(BaseModel):
    """Result of selecting the 7th element (1-based position)."""

    value: float = Field(..., description="The value of the 7th element in the list")
    index: int = Field(
        ...,
        description="0-based Python index (always 6 for the 7th element)",
        examples=[6],
    )
    position: int = Field(
        ...,
        description="1-based human position number (7 for the 7th element)",
        examples=[7],
    )


class StatisticsResponse(BaseModel):
    """Aggregate statistics for a numeric list."""

    count: int
    minimum: float
    maximum: float
    total: float
    average: float


class FilterResponse(BaseModel):
    """Filtered values that meet a minimum threshold."""

    minimum: float
    original_count: int
    filtered_count: int
    values: list[float]
