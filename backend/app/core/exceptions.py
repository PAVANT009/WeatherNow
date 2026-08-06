"""Application-level errors mapped to structured HTTP responses.

Services raise ``AppError``; FastAPI turns them into JSON with shape::

    {"detail": {"code": "...", "message": "..."}}
"""

from __future__ import annotations


class AppError(Exception):
    """Domain / API error with a stable machine-readable code."""

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_detail(self) -> dict[str, str]:
        """Return the nested ``detail`` payload used in API responses."""
        return {"code": self.code, "message": self.message}
