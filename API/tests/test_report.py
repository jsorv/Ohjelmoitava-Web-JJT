import json
from urllib import response
import pytest
from datetime import datetime, timedelta, timezone
from API.weatherradar import db, create_app
from API.weatherradar.models import WeatherReport, Location


@pytest.fixture
def client():
    """Pytest fixture to set up a test client with a clean database."""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config)
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
    report1 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="report",
        report_time=datetime.now() + timedelta(minutes=-15),
        temperature=20.5,
        humidity=60,
        wind_speed=5.0,
        cloud_cover=50,
        rain=False,
        fog=False,
    )
    report2 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="report",
        report_time=datetime.now() + timedelta(minutes=-30),
        temperature=18.0,
        humidity=70,
        wind_speed=3.0,
        cloud_cover=70,
        rain=True,
        fog=False,
    )
    report3 = WeatherReport(
        location=location,
        location_id=location.location_id,
        entry_type="report",
        report_time=datetime.now() + timedelta(minutes=-45),
        temperature=22.0,
        humidity=55,
        wind_speed=4.0,
        cloud_cover=20,
        rain=False,
        fog=False,
    )
    db.session.add_all([location, report1, report2, report3])
    db.session.commit()


def _get_valid_weather_report():
    """Helper function to return a valid weather report dictionary."""
    return {
        "location_id": 1,
        "entry_type": "report",
        "report_time": datetime.now(timezone.utc).isoformat(),
        "temperature": 20.5,
        "humidity": 60,
        "wind_speed": 5.0,
        "cloud_cover": 50,
        "rain": False,
        "fog": False,
    }


class TestReport(object):

    RESOURCE_URL = "/weatherradar/api/locations/1/reports/"

    def test_get(self, client):
        """Test retrieving all weather reports for a location."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 3
        for item in body:
            assert "report_id" in item
            assert "location_id" in item
            assert "entry_type" in item
            assert "report_time" in item
            assert "temperature" in item
            assert "humidity" in item
            assert "wind_speed" in item
            assert "cloud_cover" in item
            assert "rain" in item
            assert "fog" in item

    def test_post_valid(self, client):
        """Test creating a new weather report with valid data."""
        valid = _get_valid_weather_report()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert "Location" in resp.headers

        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

    def test_post_invalid_media_type(self, client):
        """Test creating a new weather report with an invalid media type."""
        valid = _get_valid_weather_report()
        resp = client.post(
            self.RESOURCE_URL, data=json.dumps(valid), content_type="text/plain"
        )
        assert resp.status_code == 415

    def test_post_invalid_json(self, client):
        """Test creating a new weather report with invalid JSON."""
        valid = _get_valid_weather_report()
        valid.pop("temperature")
        resp = client.post(
            self.RESOURCE_URL, data="not a json", content_type="application/json"
        )
        assert resp.status_code == 400

    def test_post_conflict(self, client):
        """Test creating a new weather report that conflicts with an existing one."""
        existing = WeatherReport.query.filter_by(
            location_id=1, entry_type="report"
        ).first()
        assert existing is not None

        valid = _get_valid_weather_report()
        valid["report_time"] = existing.report_time.isoformat()

        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409


class TestReportItem(object):

    RESOURCE_URL = "/weatherradar/api/locations/1/reports/1/"
    INVALID_URL = "/weatherradar/api/locations/1/reports/999/"
    BASE_URL = "/weatherradar/api/locations/1/reports/"

    def test_get(self, client):
        """Test retrieving a specific weather report."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

        body = json.loads(resp.data)
        assert "report_id" in body
        assert "report_time" in body

        # invalid URL
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put_valid(self, client):
        """Test updating an existing weather report with valid data."""
        valid = _get_valid_weather_report()
        valid["temperature"] = 25.0
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["temperature"] == 25.0

    def test_put_invalid_media_type(self, client):
        """Test updating an existing weather report with an invalid media type."""
        valid = _get_valid_weather_report()
        resp = client.put(
            self.RESOURCE_URL, data=json.dumps(valid), content_type="text/plain"
        )
        assert resp.status_code == 415

    def test_put_invalid_json(self, client):
        """Test updating an existing weather report with invalid JSON."""
        resp = client.put(
            self.RESOURCE_URL, data="not a json", content_type="application/json"
        )
        assert resp.status_code == 400

    def test_put_conflict(self, client):
        """Test updating an existing weather report to a state that conflicts with another report."""
        reports = WeatherReport.query.filter_by(
            location_id=1, entry_type="report"
        ).all()
        assert len(reports) >= 2

        target = reports[0]
        other = reports[1]

        item_url = f"{self.BASE_URL}{target.report_id}/"

        valid = _get_valid_weather_report()
        valid["report_time"] = (
            other.report_time.isoformat()
        )  # same as another existing report
        resp = client.put(item_url, json=valid)
        assert resp.status_code == 409

    def test_delete(self, client):
        """Test deleting an existing weather report."""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 200

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
