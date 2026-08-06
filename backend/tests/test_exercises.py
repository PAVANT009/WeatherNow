"""Tests for educational exercise endpoints (Stage 4)."""

from fastapi.testclient import TestClient


def test_seventh_element_success(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/seventh-element",
        json={"values": [12, 18, 21, 24, 27, 29, 31, 33]},
    )
    assert response.status_code == 200
    assert response.json() == {"value": 31, "index": 6, "position": 7}


def test_seventh_element_too_short_returns_422(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/seventh-element",
        json={"values": [1, 2, 3, 4, 5, 6]},
    )
    assert response.status_code == 422


def test_statistics_success(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/statistics",
        json={"values": [10, 20, 30]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 3
    assert payload["minimum"] == 10
    assert payload["maximum"] == 30
    assert payload["total"] == 60
    assert payload["average"] == 20


def test_statistics_empty_list_returns_422(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/statistics",
        json={"values": []},
    )
    assert response.status_code == 422


def test_filter_by_minimum(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/filter?minimum=20",
        json={"values": [10, 20, 15, 25, 30]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["minimum"] == 20
    assert payload["original_count"] == 5
    assert payload["filtered_count"] == 3
    assert payload["values"] == [20, 25, 30]


def test_filter_requires_minimum_query(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/v1/exercises/filter",
        json={"values": [1, 2, 3]},
    )
    assert response.status_code == 422
