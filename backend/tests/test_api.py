"""API integration tests for Stage 3 (health, cities, districts).

Uses the real PostgreSQL database and seed data. Does not call external
weather providers.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.models import City, District


def test_health_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_list_cities_includes_bengaluru(
    client: TestClient,
    seeded_city: dict[str, int],
) -> None:
    response = client.get("/api/v1/cities")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert any(city["id"] == seeded_city["city_id"] for city in payload)
    assert any(city["name"] == "Bengaluru" for city in payload)


def test_get_city_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/cities/999999")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "CITY_NOT_FOUND"
    assert "message" in detail


def test_list_districts_for_city(
    client: TestClient,
    seeded_city: dict[str, int],
) -> None:
    city_id = seeded_city["city_id"]
    response = client.get(f"/api/v1/cities/{city_id}/districts")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 12
    names = {item["name"] for item in payload}
    assert "Koramangala" in names
    assert "Indiranagar" in names
    assert "Whitefield" in names
    assert "HSR Layout" in names
    assert all(item["city_id"] == city_id for item in payload)


def test_list_districts_city_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/cities/999999/districts")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "CITY_NOT_FOUND"


def test_get_district_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/districts/999999")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "DISTRICT_NOT_FOUND"
    assert "message" in detail


def test_create_city_and_district_then_cleanup(client: TestClient) -> None:
    suffix = uuid.uuid4().hex[:8]
    city_name = f"TestCity-{suffix}"

    create_city = client.post(
        "/api/v1/cities",
        json={
            "name": city_name,
            "country_code": "IN",
            "latitude": "12.9000000",
            "longitude": "77.5000000",
        },
    )
    assert create_city.status_code == 201
    city = create_city.json()
    city_id = city["id"]
    assert city["name"] == city_name

    create_district = client.post(
        "/api/v1/districts",
        json={
            "city_id": city_id,
            "name": f"TestDistrict-{suffix}",
            "latitude": "12.9100000",
            "longitude": "77.5100000",
        },
    )
    assert create_district.status_code == 201
    district = create_district.json()
    district_id = district["id"]
    assert district["city_id"] == city_id

    get_district = client.get(f"/api/v1/districts/{district_id}")
    assert get_district.status_code == 200
    assert get_district.json()["name"] == f"TestDistrict-{suffix}"

    # Cleanup so the shared seed database stays tidy
    db = SessionLocal()
    try:
        row = db.get(District, district_id)
        if row is not None:
            db.delete(row)
            db.commit()
        city_row = db.get(City, city_id)
        if city_row is not None:
            db.delete(city_row)
            db.commit()
    finally:
        db.close()


def test_invalid_district_coordinates_return_422(
    client: TestClient,
    seeded_city: dict[str, int],
) -> None:
    response = client.post(
        "/api/v1/districts",
        json={
            "city_id": seeded_city["city_id"],
            "name": "BadCoords",
            "latitude": "120.0",
            "longitude": "77.0",
        },
    )
    assert response.status_code == 422


def test_empty_district_name_returns_422(
    client: TestClient,
    seeded_city: dict[str, int],
) -> None:
    response = client.post(
        "/api/v1/districts",
        json={
            "city_id": seeded_city["city_id"],
            "name": "   ",
            "latitude": "12.9",
            "longitude": "77.5",
        },
    )
    assert response.status_code == 422
