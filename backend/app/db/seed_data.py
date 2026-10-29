"""Static seed dataset for Indian cities and localities.

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


BENGALURU_SEED: CitySeed = {
    "name": "Bengaluru",
    "country_code": "IN",
    "latitude": "12.9716000",
    "longitude": "77.5946000",
    "districts": [
        {"name": "Koramangala", "latitude": "12.9352000", "longitude": "77.6245000"},
        {"name": "Indiranagar", "latitude": "12.9784000", "longitude": "77.6408000"},
        {"name": "Whitefield", "latitude": "12.9698000", "longitude": "77.7500000"},
        {"name": "Jayanagar", "latitude": "12.9299000", "longitude": "77.5827000"},
        {"name": "HSR Layout", "latitude": "12.9116000", "longitude": "77.6389000"},
        {"name": "Hebbal", "latitude": "13.0358000", "longitude": "77.5970000"},
        {"name": "Yelahanka", "latitude": "13.1007000", "longitude": "77.5963000"},
        {"name": "Malleshwaram", "latitude": "13.0035000", "longitude": "77.5700000"},
        {"name": "Rajajinagar", "latitude": "12.9911000", "longitude": "77.5526000"},
        {"name": "Marathahalli", "latitude": "12.9591000", "longitude": "77.6974000"},
        {"name": "Electronic City", "latitude": "12.8456000", "longitude": "77.6603000"},
        {"name": "Banashankari", "latitude": "12.9255000", "longitude": "77.5468000"},
    ],
}

MUMBAI_SEED: CitySeed = {
    "name": "Mumbai",
    "country_code": "IN",
    "latitude": "19.0760000",
    "longitude": "72.8777000",
    "districts": [
        {"name": "Colaba", "latitude": "18.9067000", "longitude": "72.8147000"},
        {"name": "Bandra", "latitude": "19.0596000", "longitude": "72.8295000"},
        {"name": "Andheri", "latitude": "19.1136000", "longitude": "72.8697000"},
        {"name": "Juhu", "latitude": "19.0988000", "longitude": "72.8264000"},
        {"name": "Powai", "latitude": "19.1176000", "longitude": "72.9060000"},
        {"name": "Dadar", "latitude": "19.0178000", "longitude": "72.8478000"},
        {"name": "Worli", "latitude": "19.0163000", "longitude": "72.8171000"},
        {"name": "Borivali", "latitude": "19.2307000", "longitude": "72.8567000"},
        {"name": "Ghatkopar", "latitude": "19.0860000", "longitude": "72.9090000"},
        {"name": "Chembur", "latitude": "19.0522000", "longitude": "72.8995000"},
    ],
}

DELHI_SEED: CitySeed = {
    "name": "Delhi",
    "country_code": "IN",
    "latitude": "28.6139000",
    "longitude": "77.2090000",
    "districts": [
        {"name": "Connaught Place", "latitude": "28.6315000", "longitude": "77.2167000"},
        {"name": "South Extension", "latitude": "28.5729000", "longitude": "77.2207000"},
        {"name": "Dwarka", "latitude": "28.5921000", "longitude": "77.0460000"},
        {"name": "Rohini", "latitude": "28.7495000", "longitude": "77.0565000"},
        {"name": "Hauz Khas", "latitude": "28.5494000", "longitude": "77.2001000"},
        {"name": "Karol Bagh", "latitude": "28.6517000", "longitude": "77.1906000"},
        {"name": "Vasant Kunj", "latitude": "28.5283000", "longitude": "77.1517000"},
        {"name": "Saket", "latitude": "28.5244000", "longitude": "77.2167000"},
        {"name": "Chandni Chowk", "latitude": "28.6506000", "longitude": "77.2303000"},
        {"name": "Mayur Vihar", "latitude": "28.6096000", "longitude": "77.2996000"},
    ],
}

HYDERABAD_SEED: CitySeed = {
    "name": "Hyderabad",
    "country_code": "IN",
    "latitude": "17.3850000",
    "longitude": "78.4867000",
    "districts": [
        {"name": "HITEC City", "latitude": "17.4435000", "longitude": "78.3772000"},
        {"name": "Gachibowli", "latitude": "17.4401000", "longitude": "78.3489000"},
        {"name": "Banjara Hills", "latitude": "17.4156000", "longitude": "78.4357000"},
        {"name": "Jubilee Hills", "latitude": "17.4319000", "longitude": "78.4073000"},
        {"name": "Madhapur", "latitude": "17.4483000", "longitude": "78.3915000"},
        {"name": "Secunderabad", "latitude": "17.4399000", "longitude": "78.4983000"},
        {"name": "Kondapur", "latitude": "17.4699000", "longitude": "78.3578000"},
        {"name": "Kukatpally", "latitude": "17.4933000", "longitude": "78.3980000"},
        {"name": "Begumpet", "latitude": "17.4447000", "longitude": "78.4664000"},
        {"name": "Charminar", "latitude": "17.3616000", "longitude": "78.4747000"},
    ],
}

CHENNAI_SEED: CitySeed = {
    "name": "Chennai",
    "country_code": "IN",
    "latitude": "13.0827000",
    "longitude": "80.2707000",
    "districts": [
        {"name": "T. Nagar", "latitude": "13.0418000", "longitude": "80.2341000"},
        {"name": "Adyar", "latitude": "13.0012000", "longitude": "80.2565000"},
        {"name": "Velachery", "latitude": "12.9815000", "longitude": "80.2180000"},
        {"name": "Anna Nagar", "latitude": "13.0850000", "longitude": "80.2101000"},
        {"name": "Mylapore", "latitude": "13.0368000", "longitude": "80.2676000"},
        {"name": "Thiruvanmiyur", "latitude": "12.9830000", "longitude": "80.2594000"},
        {"name": "Nungambakkam", "latitude": "13.0569000", "longitude": "80.2425000"},
        {"name": "Guindy", "latitude": "13.0067000", "longitude": "80.2025000"},
    ],
}

INDIAN_CITIES_SEED: list[CitySeed] = [
    BENGALURU_SEED,
    MUMBAI_SEED,
    DELHI_SEED,
    HYDERABAD_SEED,
    CHENNAI_SEED,
]


def as_decimal(value: str) -> Decimal:
    """Convert a seed coordinate/temperature string to Decimal."""
    return Decimal(value)
