import json
import pytest
from API.src.weatherradar import db, create_app
from API.src.weatherradar.models import Location


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
    location1 = Location(
        country="Finland",
        city="Oulu",
        latitude=65.01,
        longitude=25.46,
    )

    location2 = Location(
        country="Finland",
        city="Helsinki",
        latitude=60.16,
        longitude=24.93,
    )

    location3 = Location(
        country="Finland",
        city="Tampere",
        latitude=61.49,
        longitude=23.76,
    )

    db.session.add_all([location1, location2, location3])
    db.session.commit()


def _get_valid_location():
    """Helper function to return a valid location dictionary."""
    return {
        "country": "Sweden",
        "city": "Stockholm",
        "latitude": 59.33,
        "longitude": 18.06,
    }


class TestLocation(object):
    """Test suite for the Location resources."""

    RESOURCE_URL = "/weatherradar/api/locations/"

    def test_get(self, client):
        """Test retrieving all locations."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert len(body) == 3
        for item in body:
            assert "country" in item
            assert "city" in item
            assert "latitude" in item
            assert "longitude" in item

    def test_post_valid(self, client):
        """Test creating a new location with valid data."""
        valid = _get_valid_location()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert "Location" in resp.headers

        # Verify resource exists
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200

    def test_post_invalid_media_type(self, client):
        """Test creating a new location with an invalid media type."""
        valid = _get_valid_location()
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

    def test_post_invalid_json(self, client):
        """Test creating a new location with invalid JSON data."""
        valid = _get_valid_location()
        valid.pop("country")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    def test_post_conflict(self, client):
        """Test creating a new location that conflicts with an existing one."""
        valid = {
            "country": "Finland",
            "city": "Helsinki",  # already exists as location 2
            "latitude": 60.16,
            "longitude": 24.93,
        }

        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409


class TestLocationItem(object):
    """Test suite for the LocationItem resources."""

    RESOURCE_URL = "/weatherradar/api/locations/1/"
    INVALID_URL = "/weatherradar/api/locations/999/"

    def test_get(self, client):
        """Test retrieving a specific location."""
        # Valid request
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200

        body = json.loads(resp.data)
        assert body["city"] == "Oulu"
        assert body["country"] == "Finland"
        assert "latitude" in body
        assert "longitude" in body

        # Invalid URL
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put_valid(self, client):
        """Test updating a specific location with valid data."""
        valid = _get_valid_location()
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

    def test_put_invalid_media_type(self, client):
        """Test updating a specific location with an invalid media type."""
        valid = _get_valid_location()
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

    def test_put_invalid_json(self, client):
        """Test updating a specific location with invalid JSON data."""
        valid = _get_valid_location()
        valid.pop("country")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

    def test_put_conflict(self, client):
        """Test updating a specific location so it conflicts with another location."""
        valid = {
            "country": "Finland",
            "city": "Helsinki",  # already exists as location 2
            "latitude": 60.16,
            "longitude": 24.93,
        }

        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

    def test_delete(self, client):
        """Test deleting a specific location."""
        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
