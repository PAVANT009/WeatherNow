"""City data-access helpers (SQLAlchemy queries only)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import City
from app.schemas.city import CityCreate


def list_cities(db: Session) -> list[City]:
    """Return cities ordered by name then id."""
    return list(db.scalars(select(City).order_by(City.name, City.id)).all())


def get_city_by_id(db: Session, city_id: int) -> City | None:
    """Return a city by primary key, or ``None`` if missing."""
    return db.get(City, city_id)


def get_city_by_name_country(
    db: Session,
    name: str,
    country_code: str,
) -> City | None:
    """Return a city matched by unique (name, country_code)."""
    return db.scalar(
        select(City).where(
            City.name == name,
            City.country_code == country_code,
        )
    )


def create_city(db: Session, payload: CityCreate) -> City:
    """Insert a city row and refresh it so defaults (id, created_at) are loaded."""
    city = City(
        name=payload.name,
        country_code=payload.country_code,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )
    db.add(city)
    db.commit()
    db.refresh(city)
    return city
