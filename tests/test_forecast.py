import json
import pytest
from datetime import datetime, timedelta
from API.src.weatherradar import db, create_app
from API.src.weatherradar.models import WeatherReport, Location


@pytest.fixture
def client():
    """Pytest fixture to set up a test client with a clean database."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    db.create_all()
    _populate_db()

    yield app.test_client()

    db.session.rollback()
    db.drop_all()
    db.session.remove()
    ctx.pop()


def _populate_db():
    """Helper function to populate the database with test data."""
    location = Location(
        country="Finland",
        city="Oulu",
        latitude=65.01,
        longitude=25.46,
    )
    forecast1 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="forecast",
        report_time=datetime.now(),
        forecast_time=(datetime.now() + timedelta(hours=1)),
        temperature=20.5,
        humidity=60,
        wind_speed=5.0,
        cloud_cover=50,
        rain=False,
        fog=False,
    )
    forecast2 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="forecast",
        report_time=datetime.now(),
        forecast_time=(datetime.now() + timedelta(hours=2)),
        temperature=18.0,
        humidity=70,
        wind_speed=3.0,
        cloud_cover=70,
        rain=True,
        fog=False,
    )
    forecarst3 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="forecast",
        report_time=datetime.now(),
        forecast_time=(datetime.now() + timedelta(hours=3)),
        temperature=22.0,
        humidity=55,
        wind_speed=4.0,
        cloud_cover=20,
        rain=False,
        fog=False,
    )
    db.session.add_all([location, forecast1, forecast2, forecarst3])
    db.session.commit()


def _get_valid_weather_forecast():
    """Helper function to return a valid weather forecast dictionary."""
    return {
        "location_id": 1,
        "entry_type": "forecast",
        "report_time": datetime.now(),
        "forecast_time": (datetime.now() + timedelta(hours=4)),
        "temperature": 20.5,
        "humidity": 60,
        "wind_speed": 5.0,
        "cloud_cover": 50,
        "rain": False,
        "fog": False,
    }


class TestForecast(object):
    """Test suite for the WeatherForecasts and WeatherForecastItem resources."""

    RESOURCE_URL = "/api/locations/1/forecasts/"

    def test_get(self, client):
        """Test retrieving all forecasts for a location."""
        # Valid request should return a list of forecasts for the location
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = json.loads(response.data)
        # Verify the response contains a list of forecasts with the expected fields
        assert len(data) == 3
        for item in data:
            assert "location_id" in item
            assert "entry_type" in item
            assert "report_time" in item
            assert "forecast_time" in item
            assert "temperature" in item
            assert "humidity" in item
            assert "wind_speed" in item
            assert "cloud_cover" in item
            assert "rain" in item
            assert "fog" in item

    def test_post_valid(self, client):
        """Test creating a new forecast with valid data."""
        # Create a new forecast with valid data (should succeed)
        valid = _get_valid_weather_forecast()
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 201
        assert "Location" in response.headers

        # Verify resource exists
        resp = client.get(response.headers["Location"])
        assert resp.status_code == 200

    def test_post_invalid_media_type(self, client):
        """Test creating a new forecast with an invalid media type."""
        # Convert datetime objects to ISO format strings for JSON serialization
        valid = _get_valid_weather_forecast()
        valid["report_time"] = valid["report_time"].isoformat()
        valid["forecast_time"] = valid["forecast_time"].isoformat()
        # Try to create the forecast with invalid media type (should fail)
        response = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

    def test_post_invalid_json(self, client):
        """Test creating a new forecast with invalid JSON data."""
        # Remove a required field to make the JSON invalid
        valid = _get_valid_weather_forecast()
        valid.pop("temperature")
        # Try to create the forecast with invalid JSON (should fail)
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 400

    def test_post_conflict(self, client):
        """Test creating a new forecast that conflicts with an existing one."""
        # Create a forecast with a known time (should succeed)
        valid = _get_valid_weather_forecast()
        valid["forecast_time"] = datetime.now() + timedelta(hours=1)
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 201

        # Try to post the same forecast again (should conflict)
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 409


class TestForecastItem(object):

    RESOURCE_URL = "/api/locations/1/forecasts/1/"
    INVALID_URL = "/api/locations/1/forecasts/999/"

    def test_get(self, client):
        """Test retrieving a specific forecast for a location."""
        # Valid request should return the forecast
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200

        # Verify the response contains the expected forecast data
        body = json.loads(response.data)
        assert body["location_id"] == 1
        assert body["entry_type"] == "forecast"
        assert "report_time" in body
        assert "forecast_time" in body
        assert "temperature" in body
        assert "humidity" in body
        assert "wind_speed" in body
        assert "cloud_cover" in body
        assert "rain" in body
        assert "fog" in body

    def test_put_valid(self, client):
        """Test updating a specific forecast with valid data."""
        # Update the forecast with valid data
        valid = _get_valid_weather_forecast()
        response = client.put(self.RESOURCE_URL, json=valid)
        assert response.status_code == 204

        # Verify resource was updated
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        body = json.loads(response.data)
        assert body["temperature"] == valid["temperature"]
        assert body["humidity"] == valid["humidity"]
        assert body["wind_speed"] == valid["wind_speed"]
        assert body["cloud_cover"] == valid["cloud_cover"]
        assert body["rain"] == valid["rain"]
        assert body["fog"] == valid["fog"]

    def test_put_invalid_media_type(self, client):
        """Test updating a specific forecast with an invalid media type."""
        valid = _get_valid_weather_forecast()
        # Convert datetime objects to ISO format strings for JSON serialization
        valid["report_time"] = valid["report_time"].isoformat()
        valid["forecast_time"] = valid["forecast_time"].isoformat()
        # Try to update the forecast with invalid media type (should fail)
        response = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

    def test_put_invalid_json(self, client):
        """Test updating a specific forecast with invalid JSON data."""
        valid = _get_valid_weather_forecast()
        # Remove a required field to make the JSON invalid
        valid.pop("temperature")
        # Try to update the forecast with invalid JSON (should fail)
        response = client.put(self.RESOURCE_URL, json=valid)
        assert response.status_code == 400

    def test_put_conflict(self, client):
        """Test updating a specific forecast to a time that conflicts with another forecast."""
        valid = _get_valid_weather_forecast()
        conflict = _get_valid_weather_forecast()
        time = datetime.now() + timedelta(hours=2)
        valid["forecast_time"] = time
        # Update the forecast to a known time (should succeed)
        response = client.put(self.RESOURCE_URL, json=valid)
        assert response.status_code == 204

        # Try to update another forecast to the same time (should conflict)
        conflict["forecast_time"] = time
        conflict["report_id"] = 2
        response = client.put("/api/locations/1/forecasts/2/", json=conflict)
        assert response.status_code == 409

    def test_delete(self, client):
        """Test deleting a specific forecast for a location."""
        # Delete the forecast
        response = client.delete(self.RESOURCE_URL)
        assert response.status_code == 204

        # Verify resource was deleted
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 404
