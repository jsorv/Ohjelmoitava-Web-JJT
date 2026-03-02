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
        "report_time": datetime.now(),
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
        # TODO
        pass

    def test_post_valid(self, client):
        # TODO
        pass

    def test_post_invalid_media_type(self, client):
        # TODO
        pass

    def test_post_invalid_json(self, client):
        # TODO
        pass

    def test_post_conflict(self, client):
        # TODO
        pass


class TestReportItem(object):

    RESOURCE_URL = "/weatherradar/api/locations/1/reports/1/"
    INVALID_URL = "/weatherradar/api/locations/1/reports/999/"

    def test_get(self, client):
        # TODO
        pass

    def test_put_valid(self, client):
        # TODO
        pass

    def test_put_invalid_media_type(self, client):
        # TODO
        pass

    def test_put_invalid_json(self, client):
        # TODO
        pass

    def test_put_conflict(self, client):
        # TODO
        pass

    def test_delete(self, client):
        # TODO
        pass
