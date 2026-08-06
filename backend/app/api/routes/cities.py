"""City routes: list, get by id, and create."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.city import CityCreate, CityRead
from app.services import city as city_service

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)) -> list[CityRead]:
    """List all cities in the catalog."""
    return [CityRead.model_validate(city) for city in city_service.list_cities(db)]


@router.get("/{city_id}", response_model=CityRead)
def get_city(city_id: int, db: Session = Depends(get_db)) -> CityRead:
    """Return a single city by id."""
    return CityRead.model_validate(city_service.get_city(db, city_id))


@router.post("", response_model=CityRead, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)) -> CityRead:
    """Create a new city."""
    return CityRead.model_validate(city_service.create_city(db, payload))
