"""City service: orchestration and domain errors on top of the repository."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import City
from app.repositories import city as city_repository
from app.schemas.city import CityCreate


def list_cities(db: Session) -> list[City]:
    """Return all cities."""
    return city_repository.list_cities(db)


def get_city(db: Session, city_id: int) -> City:
    """Return one city or raise CITY_NOT_FOUND."""
    city = city_repository.get_city_by_id(db, city_id)
    if city is None:
        raise AppError(
            code="CITY_NOT_FOUND",
            message="City could not be found",
            status_code=404,
        )
    return city


def create_city(db: Session, payload: CityCreate) -> City:
    """Create a city; map unique violations to HTTP 409."""
    existing = city_repository.get_city_by_name_country(
        db,
        payload.name,
        payload.country_code,
    )
    if existing is not None:
        raise AppError(
            code="CITY_ALREADY_EXISTS",
            message=(
                f"City '{payload.name}' already exists "
                f"for country '{payload.country_code}'"
            ),
            status_code=409,
        )

    try:
        return city_repository.create_city(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            code="CITY_ALREADY_EXISTS",
            message=(
                f"City '{payload.name}' already exists "
                f"for country '{payload.country_code}'"
            ),
            status_code=409,
        ) from exc
