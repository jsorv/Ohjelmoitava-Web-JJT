import json
import pytest
from datetime import datetime, timedelta
from API.src.weatherradar import db, create_app
from API.src.weatherradar.models import WeatherReport, Location


@pytest.fixture
def client():
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

    RESOURCE_URL = "/api/locations/1/forecasts/"

    def test_get(self, client):
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200
        data = json.loads(response.data)
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
        valid = _get_valid_weather_forecast()
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 201
        assert "Location" in response.headers

        # Verify resource exists
        resp = client.get(response.headers["Location"])
        assert resp.status_code == 200

    def test_post_invalid_media_type(self, client):
        valid = _get_valid_weather_forecast()
        valid["report_time"] = valid["report_time"].isoformat()
        valid["forecast_time"] = valid["forecast_time"].isoformat()
        response = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

    def test_post_invalid_json(self, client):
        valid = _get_valid_weather_forecast()
        valid.pop("temperature")
        response = client.post(self.RESOURCE_URL, json=valid)
        assert response.status_code == 400

    def test_post_conflict(self, client):
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
        # Valid request
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 200

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
        valid = _get_valid_weather_forecast()
        valid["report_time"] = valid["report_time"].isoformat()
        valid["forecast_time"] = valid["forecast_time"].isoformat()
        response = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert response.status_code == 415

    def test_put_invalid_json(self, client):
        valid = _get_valid_weather_forecast()
        valid.pop("temperature")
        response = client.put(self.RESOURCE_URL, json=valid)
        assert response.status_code == 400

    def test_put_conflict(self, client):
        valid = _get_valid_weather_forecast()
        conflict = _get_valid_weather_forecast()
        time = datetime.now() + timedelta(hours=2)
        valid["forecast_time"] = time
        response = client.put(self.RESOURCE_URL, json=valid)
        assert response.status_code == 204

        # Try to update another forecast to the same time (should conflict)
        conflict["forecast_time"] = time
        conflict["report_id"] = 2
        response = client.put("/api/locations/1/forecasts/2/", json=conflict)
        assert response.status_code == 409

    def test_delete(self, client):
        response = client.delete(self.RESOURCE_URL)
        assert response.status_code == 204

        # Verify resource was deleted
        response = client.get(self.RESOURCE_URL)
        assert response.status_code == 404
