"""Static seed dataset for initial development.

Coordinates are kept here (not scattered across services) so they remain
easy to review and update.
"""

from decimal import Decimal
from typing import TypedDict


class DistrictSeed(TypedDict):
    name: str
    latitude: str
    longitude: str


class CitySeed(TypedDict):
    name: str
    country_code: str
    latitude: str
    longitude: str
    districts: list[DistrictSeed]


# Approximate WGS84 coordinates for all 12 Çanakkale districts.
CANAKKALE_SEED: CitySeed = {
    "name": "Çanakkale",
    "country_code": "TR",
    "latitude": "40.1553000",
    "longitude": "26.4142000",
    "districts": [
        {
            "name": "Merkez",
            "latitude": "40.1553000",
            "longitude": "26.4142000",
        },
        {
            "name": "Ayvacık",
            "latitude": "39.6011000",
            "longitude": "26.4047000",
        },
        {
            "name": "Bayramiç",
            "latitude": "39.8089000",
            "longitude": "26.6131000",
        },
        {
            "name": "Biga",
            "latitude": "40.2281000",
            "longitude": "27.2422000",
        },
        {
            "name": "Bozcaada",
            "latitude": "39.8350000",
            "longitude": "26.0697000",
        },
        {
            "name": "Çan",
            "latitude": "40.0278000",
            "longitude": "27.0525000",
        },
        {
            "name": "Eceabat",
            "latitude": "40.1842000",
            "longitude": "26.3575000",
        },
        {
            "name": "Ezine",
            "latitude": "39.7856000",
            "longitude": "26.3408000",
        },
        {
            "name": "Gelibolu",
            "latitude": "40.4103000",
            "longitude": "26.6708000",
        },
        {
            "name": "Gökçeada",
            "latitude": "40.1931000",
            "longitude": "25.9089000",
        },
        {
            "name": "Lapseki",
            "latitude": "40.3442000",
            "longitude": "26.6858000",
        },
        {
            "name": "Yenice",
            "latitude": "39.9308000",
            "longitude": "27.2581000",
        },
    ],
}


def as_decimal(value: str) -> Decimal:
    """Convert a seed coordinate/temperature string to Decimal."""
    return Decimal(value)
