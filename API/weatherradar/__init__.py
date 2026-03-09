"""Weather radar API package."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    """Application factory function for the weather radar API."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///"
        + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # import here
    from .api import api_bp
    from .utils import LocationConverter
    from .utils import ForecastConverter
    from .utils import ReportConverter

    app.url_map.converters["location"] = LocationConverter
    app.url_map.converters["forecast"] = ForecastConverter
    app.url_map.converters["report"] = ReportConverter

    app.register_blueprint(api_bp)

    return app
