"""Educational exercise routes (list algorithms over JSON).

Prefix (after ``/api/v1``): ``/exercises``

Endpoints are independent of weather data; they practice JSON I/O and
Python indexing / aggregation.
"""

from fastapi import APIRouter, Query

from app.schemas.exercises import (
    FilterResponse,
    NumberListRequest,
    SeventhElementRequest,
    SeventhElementResponse,
    StatisticsResponse,
)
from app.services import exercises as exercises_service

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.post("/seventh-element", response_model=SeventhElementResponse)
def seventh_element(payload: SeventhElementRequest) -> SeventhElementResponse:
    """Return the 7th element of the list.

    Rules:
    - List must contain at least 7 elements (otherwise Pydantic returns 422).
    - Because Python uses 0-based indexing, the 7th element has index 6.
    """
    return exercises_service.get_seventh_element(payload.values)


@router.post("/statistics", response_model=StatisticsResponse)
def statistics(payload: NumberListRequest) -> StatisticsResponse:
    """Compute min, max, sum, average, and count for the supplied number list."""
    return exercises_service.compute_statistics(payload.values)


@router.post("/filter", response_model=FilterResponse)
def filter_values(
    payload: NumberListRequest,
    minimum: float = Query(
        ...,
        description="Values smaller than this are filtered out (>= minimum are kept)",
        examples=[20],
    ),
) -> FilterResponse:
    """Filter list based on the minimum query parameter threshold."""
    return exercises_service.filter_by_minimum(payload.values, minimum)
