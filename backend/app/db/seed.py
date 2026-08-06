"""Database seed helpers.

Run from the backend directory:

    python -m app.db.seed
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.seed_data import CANAKKALE_SEED, as_decimal
from app.db.session import SessionLocal
from app.models import City, District


def seed_canakkale(db: Session) -> City:
    """Insert Çanakkale and ensure all seed districts exist.

    Existing cities are not duplicated. Missing districts are added so the
    catalog can grow from 6 to all 12 districts without wiping data.
    """
    city = db.scalar(
        select(City).where(
            City.name == CANAKKALE_SEED["name"],
            City.country_code == CANAKKALE_SEED["country_code"],
        )
    )

    if city is None:
        city = City(
            name=CANAKKALE_SEED["name"],
            country_code=CANAKKALE_SEED["country_code"],
            latitude=as_decimal(CANAKKALE_SEED["latitude"]),
            longitude=as_decimal(CANAKKALE_SEED["longitude"]),
        )
        db.add(city)
        db.flush()
        print(f"Created city '{city.name}' (id={city.id}).")
    else:
        print(f"City '{city.name}' already exists (id={city.id}).")

    existing_names = {district.name for district in city.districts}
    added = 0
    for district_data in CANAKKALE_SEED["districts"]:
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
        print(f"Added {added} new district(s). Total: {len(city.districts)}.")
    else:
        print(f"No new districts needed. Total: {len(city.districts)}.")

    return city


def main() -> None:
    """CLI entrypoint for seeding the development database."""
    db = SessionLocal()
    try:
        seed_canakkale(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
