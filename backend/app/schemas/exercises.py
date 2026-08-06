"""Pydantic schemas for educational / training exercise endpoints."""

from pydantic import BaseModel, Field


class NumberListRequest(BaseModel):
    """A JSON body carrying a list of numbers for exercise endpoints."""

    values: list[float] = Field(
        ...,
        min_length=1,
        description="Sayı dizisi (JSON array). Örnek: [12, 18, 21, 24, 27, 29, 31, 33]",
        examples=[[12, 18, 21, 24, 27, 29, 31, 33]],
    )


class SeventhElementRequest(BaseModel):
    """Request for the '7th element' algorithm exercise."""

    values: list[float] = Field(
        ...,
        min_length=7,
        description=(
            "En az 7 elemanlı sayı listesi. "
            "Python listelerinde indeks 0'dan başlar; bu yüzden 7. elemanın indeksi 6'dır."
        ),
        examples=[[12, 18, 21, 24, 27, 29, 31, 33]],
    )


class SeventhElementResponse(BaseModel):
    """Result of selecting the 7th element (1-based position)."""

    value: float = Field(..., description="Listedeki 7. elemanın değeri")
    index: int = Field(
        ...,
        description="0 tabanlı Python indeksi (7. eleman için her zaman 6)",
        examples=[6],
    )
    position: int = Field(
        ...,
        description="1 tabanlı insan konum numarası (7. eleman için 7)",
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
