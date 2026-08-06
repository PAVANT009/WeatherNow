"""District routes nested under cities plus get-by-id and create."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.district import DistrictCreate, DistrictRead
from app.services import district as district_service

router = APIRouter(tags=["districts"])


@router.get(
    "/cities/{city_id}/districts",
    response_model=list[DistrictRead],
)
def list_districts_for_city(
    city_id: int,
    db: Session = Depends(get_db),
) -> list[DistrictRead]:
    """List districts that belong to the given city."""
    districts = district_service.list_districts_for_city(db, city_id)
    return [DistrictRead.model_validate(item) for item in districts]


@router.get("/districts/{district_id}", response_model=DistrictRead)
def get_district(district_id: int, db: Session = Depends(get_db)) -> DistrictRead:
    """Return a single district by id."""
    return DistrictRead.model_validate(district_service.get_district(db, district_id))


@router.post(
    "/districts",
    response_model=DistrictRead,
    status_code=status.HTTP_201_CREATED,
)
def create_district(
    payload: DistrictCreate,
    db: Session = Depends(get_db),
) -> DistrictRead:
    """Create a district linked to an existing city."""
    return DistrictRead.model_validate(district_service.create_district(db, payload))
