import pytest
from app import app, julian_to_unix, unix_to_julian
import json


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_julian_conversion():
    assert round(julian_to_unix(2440587.5), 0) == 0  # Epoch check
    assert unix_to_julian(0) == 2440587.5


def test_create_marker_success(client, mocker):
    mock_response = {
        "id": "123",
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
        "message": "Test",
        "type": "test",
    }
    mocker.patch("libhoney.client.Client.create_marker", return_value=mock_response)

    data = {"start_time": 2440587.5, "message": "Test"}
    response = client.post("/createMarker", json=data)
    assert response.status_code == 201
    assert response.json["id"] == "123"
    assert response.json["starttime"] == 2440587.5


def test_missing_fields(client):
    response = client.post("/createMarker", json={"start_time": 2440587.5})
    assert response.status_code == 400


def test_invalid_julian(client):
    response = client.post(
        "/createMarker", json={"start_time": "invalid", "message": "Test"}
    )
    assert response.status_code == 400
