"""Database seed helpers for Indian cities and localities.

Run from the backend directory:

    python -m app.db.seed
"""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.seed_data import INDIAN_CITIES_SEED, BENGALURU_SEED, as_decimal
from app.db.session import SessionLocal
from app.models import City, District, WeatherRecord


def cleanup_non_indian_cities(db: Session) -> int:
    """Remove legacy/foreign cities and their dependent records."""
    non_in_cities = list(db.scalars(select(City).where(City.country_code != "IN")).all())
    if not non_in_cities:
        return 0

    removed = 0
    for city in non_in_cities:
        district_ids = list(
            db.scalars(select(District.id).where(District.city_id == city.id)).all()
        )
        if district_ids:
            # Delete dependent weather records first
            db.execute(
                delete(WeatherRecord).where(WeatherRecord.district_id.in_(district_ids))
            )
            # Delete districts
            db.execute(delete(District).where(District.id.in_(district_ids)))

        db.delete(city)
        removed += 1

    db.commit()
    print(f"Cleaned up {removed} legacy non-Indian city/cities.")
    return removed


def seed_single_city(db: Session, city_seed: dict) -> City:
    """Insert or update a single city and ensure all seed districts exist."""
    city = db.scalar(
        select(City).where(
            City.name == city_seed["name"],
            City.country_code == city_seed["country_code"],
        )
    )

    if city is None:
        city = City(
            name=city_seed["name"],
            country_code=city_seed["country_code"],
            latitude=as_decimal(city_seed["latitude"]),
            longitude=as_decimal(city_seed["longitude"]),
        )
        db.add(city)
        db.flush()
        print(f"Created city '{city.name}' (id={city.id}).")
    else:
        print(f"City '{city.name}' already exists (id={city.id}).")

    existing_names = {district.name for district in city.districts}
    added = 0
    for district_data in city_seed["districts"]:
        if district_data["name"] in existing_names:
            continue
        db.add(
            District(
                city_id=city.id,
                name=district_data["name"],
                latitude=as_decimal(district_data["latitude"]),
                longitude=as_decimal(district_data["longitude"]),
            )
        )
        added += 1

    db.commit()
    db.refresh(city)

    if added:
        print(f"  Added {added} new locality/localities for '{city.name}'. Total: {len(city.districts)}.")
    else:
        print(f"  All localities up to date for '{city.name}'. Total: {len(city.districts)}.")

    return city


def seed_bengaluru(db: Session) -> City:
    """Insert Bengaluru and ensure all seed districts exist."""
    return seed_single_city(db, BENGALURU_SEED)


def seed_all_indian_cities(db: Session) -> list[City]:
    """Seed all configured Indian cities and remove legacy non-Indian cities."""
    cleanup_non_indian_cities(db)
    cities = []
    for city_seed in INDIAN_CITIES_SEED:
        cities.append(seed_single_city(db, city_seed))
    return cities


def main() -> None:
    """CLI entrypoint for seeding the development database."""
    db = SessionLocal()
    try:
        seed_all_indian_cities(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
