import pytest
from API.src.weatherradar import db, create_app


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
    # Add test data to the database here
    pass


# TODO: API functionality tests
