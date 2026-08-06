"""District service: orchestration and domain errors on top of the repository."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import District
from app.repositories import city as city_repository
from app.repositories import district as district_repository
from app.schemas.district import DistrictCreate


def list_districts_for_city(db: Session, city_id: int) -> list[District]:
    """List districts for a city; 404 if the city does not exist."""
    city = city_repository.get_city_by_id(db, city_id)
    if city is None:
        raise AppError(
            code="CITY_NOT_FOUND",
            message="City could not be found",
            status_code=404,
        )
    return district_repository.list_districts_for_city(db, city_id)


def get_district(db: Session, district_id: int) -> District:
    """Return one district or raise DISTRICT_NOT_FOUND."""
    district = district_repository.get_district_by_id(db, district_id)
    if district is None:
        raise AppError(
            code="DISTRICT_NOT_FOUND",
            message="District could not be found",
            status_code=404,
        )
    return district


def create_district(db: Session, payload: DistrictCreate) -> District:
    """Create a district under an existing city; unique name → 409."""
    city = city_repository.get_city_by_id(db, payload.city_id)
    if city is None:
        raise AppError(
            code="CITY_NOT_FOUND",
            message="City could not be found",
            status_code=404,
        )

    existing = district_repository.get_district_by_city_and_name(
        db,
        payload.city_id,
        payload.name,
    )
    if existing is not None:
        raise AppError(
            code="DISTRICT_ALREADY_EXISTS",
            message=(
                f"District '{payload.name}' already exists "
                f"for city_id={payload.city_id}"
            ),
            status_code=409,
        )

    try:
        return district_repository.create_district(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            code="DISTRICT_ALREADY_EXISTS",
            message=(
                f"District '{payload.name}' already exists "
                f"for city_id={payload.city_id}"
            ),
            status_code=409,
        ) from exc
