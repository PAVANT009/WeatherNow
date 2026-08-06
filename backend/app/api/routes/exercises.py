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
    """Listenin 7. elemanını döndürür.

    Kurallar:
    - Listede en az 7 eleman olmalı (aksi halde Pydantic 422 verir).
    - Python indeksleri 0'dan başladığı için 7. elemanın indeksi 6'dır.
    """
    return exercises_service.get_seventh_element(payload.values)


@router.post("/statistics", response_model=StatisticsResponse)
def statistics(payload: NumberListRequest) -> StatisticsResponse:
    """Gönderilen sayı dizisi için min, max, toplam, ortalama ve eleman sayısı."""
    return exercises_service.compute_statistics(payload.values)


@router.post("/filter", response_model=FilterResponse)
def filter_values(
    payload: NumberListRequest,
    minimum: float = Query(
        ...,
        description="Bu değerden küçük olanlar elenir (>= minimum kalır)",
        examples=[20],
    ),
) -> FilterResponse:
    """Query parametresindeki minimum değere göre listeyi filtreler."""
    return exercises_service.filter_by_minimum(payload.values, minimum)
