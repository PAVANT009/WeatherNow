"""District data-access helpers (SQLAlchemy queries only)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import District
from app.schemas.district import DistrictCreate


def list_districts_for_city(db: Session, city_id: int) -> list[District]:
    """Return districts belonging to ``city_id``, ordered by name."""
    return list(
        db.scalars(
            select(District)
            .where(District.city_id == city_id)
            .order_by(District.name, District.id)
        ).all()
    )


def get_district_by_id(db: Session, district_id: int) -> District | None:
    """Return a district by primary key, or ``None`` if missing."""
    return db.get(District, district_id)


def get_district_by_city_and_name(
    db: Session,
    city_id: int,
    name: str,
) -> District | None:
    """Return a district matched by unique (city_id, name)."""
    return db.scalar(
        select(District).where(
            District.city_id == city_id,
            District.name == name,
        )
    )


def create_district(db: Session, payload: DistrictCreate) -> District:
    """Insert a district row and refresh it so defaults are loaded."""
    district = District(
        city_id=payload.city_id,
        name=payload.name,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(district)
    db.commit()
    db.refresh(district)
    return district
