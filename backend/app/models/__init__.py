"""ORM model exports.

Importing these modules registers tables on Base.metadata for Alembic.
"""

from app.models.weather import City, District, WeatherRecord

__all__ = ["City", "District", "WeatherRecord"]
