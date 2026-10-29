"""Business logic for educational list-processing endpoints.

These helpers are intentionally pure (no database) so students can focus on
Python indexing, JSON request bodies, and Pydantic validation.
"""

from app.schemas.exercises import (
    FilterResponse,
    SeventhElementResponse,
    StatisticsResponse,
)


def get_seventh_element(values: list[float]) -> SeventhElementResponse:
    """Return the 7th element using 0-based indexing.

    Humans count the "7th item" starting from 1 (position = 7).
    In Python lists, 0-based indexing means the 7th item is at index 6 (``values[6]``).
    """
    return SeventhElementResponse(
        value=values[6],
        index=6,
        position=7,
    )


def compute_statistics(values: list[float]) -> StatisticsResponse:
    """Compute min, max, sum, average, and count for the given numbers."""
    total = float(sum(values))
    count = len(values)
    return StatisticsResponse(
        count=count,
        minimum=float(min(values)),
        maximum=float(max(values)),
        total=total,
        average=total / count,
    )


def filter_by_minimum(values: list[float], minimum: float) -> FilterResponse:
    """Keep only values that are greater than or equal to ``minimum``."""
    filtered = [value for value in values if value >= minimum]
    return FilterResponse(
        minimum=minimum,
        original_count=len(values),
        filtered_count=len(filtered),
        values=filtered,
    )
