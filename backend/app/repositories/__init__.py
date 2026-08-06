"""Data access / repository layer.

Repositories talk to SQLAlchemy only; they do not raise HTTP errors.
"""

from app.repositories import city as city_repository
from app.repositories import district as district_repository

__all__ = ["city_repository", "district_repository"]
