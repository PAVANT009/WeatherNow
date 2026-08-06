"""Health-check business logic."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.schemas.common import HealthResponse


def get_health(db: Session) -> HealthResponse:
    """Verify the API process can reach PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise AppError(
            code="DATABASE_UNAVAILABLE",
            message="Database is temporarily unavailable",
            status_code=503,
        ) from exc

    return HealthResponse(status="ok", database="connected")
