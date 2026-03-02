from email.utils import parsedate_to_datetime
from dateutil.parser import isoparse
from sqlalchemy import text

from . import db


class Location(db.Model):
    """Model representing a geographic location."""

    __tablename__ = "locations"
    __table_args__ = (db.UniqueConstraint("country", "city", name="uq_country_city"),)

    location_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    weather_reports = db.relationship(
        "WeatherReport", back_populates="location", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """String representation of the Location model."""
        return f"<Location {self.city}, {self.country}>"

    def serialize(self):
        """Serializes the Location object to a dictionary."""
        return {
            "location_id": self.location_id,
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def deserialize(self, doc):
        """Deserializes a dictionary to populate the Location object."""
        self.country = doc["country"]
        self.city = doc["city"]
        self.latitude = doc["latitude"]
        self.longitude = doc["longitude"]

    @staticmethod
    def json_schema():
        """Returns the JSON schema for the Location model."""
        schema = {
            "type": "object",
            "required": [
                "country",
                "city",
                "latitude",
                "longitude",
            ],
        }
        props = schema["properties"] = {}
        props["country"] = {
            "description": "Name of location (country)",
            "type": "string",
        }
        props["city"] = {"description": "Name of location (city)", "type": "string"}
        props["latitude"] = {
            "description": "Geographic latitude",
            "type": "number",
            "minimum": -90,
            "maximum": 90,
        }
        props["longitude"] = {
            "description": "Geographic longitude",
            "type": "number",
            "minimum": -180,
            "maximum": 180,
        }
        return schema


class WeatherReport(db.Model):
    """Model representing a weather report or forecast for a specific location."""

    __tablename__ = "weather_reports"
    __table_args__ = (
        db.Index(
            "uq_report_loc_report_time",
            "location_id", "report_time",
            unique=True,
            sqlite_where=text("entry_type = 'report'")
        ),
        db.Index(
            "uq_forecast_loc_forecast_time",
            "location_id", "forecast_time",
            unique=True,
            sqlite_where=text("entry_type = 'forecast'")
        ),
    )

    report_id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(
        db.Integer, db.ForeignKey("locations.location_id"), nullable=False
    )

    entry_type = db.Column(
        db.Enum("report", "forecast", name="entry_type_enum"), nullable=False
    )  # "report" or "forecast"

    report_time = db.Column(db.DateTime, nullable=False)
    forecast_time = db.Column(db.DateTime, nullable=True)  # nullable true

    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer, db.CheckConstraint("humidity BETWEEN 0 AND 100"))
    wind_speed = db.Column(db.Float, db.CheckConstraint("wind_speed >= 0"))
    cloud_cover = db.Column(
        db.Integer, db.CheckConstraint("cloud_cover BETWEEN 0 AND 100")
    )
    rain = db.Column(db.Boolean, nullable=False)
    fog = db.Column(db.Boolean, nullable=False)

    location = db.relationship("Location", back_populates="weather_reports")

    def __repr__(self):
        """String representation of the WeatherReport model."""
        return f"<WeatherReport {self.entry_type} for {self.location.id} at {self.report_time}>"

    def serialize(self):
        return {
            "report_id": self.report_id,
            "location_id": self.location_id,
            "entry_type": self.entry_type,
            "report_time": self.report_time.isoformat() if self.report_time else None,
            "forecast_time": self.forecast_time.isoformat() if self.forecast_time else None,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "cloud_cover": self.cloud_cover,
            "rain": self.rain,
            "fog": self.fog,
        }
        
    def deserialize(self, data, location_id, entry_type="report"):
        """Deserializes a dictionary to populate the WeatherReport object."""
        self.location_id = location_id
        self.entry_type = entry_type
        self.report_time = isoparse(data["report_time"])
        self.forecast_time = data.get("forecast_time")
        if self.forecast_time:
            self.forecast_time = isoparse(self.forecast_time)
        self.temperature = data["temperature"]
        self.humidity = data["humidity"]
        self.wind_speed = data["wind_speed"]
        self.cloud_cover = data["cloud_cover"]
        self.rain = data["rain"]
        self.fog = data["fog"]

    @staticmethod
    def json_schema():
        """Returns the JSON schema for the WeatherReport model."""
        schema = {
            "type": "object",
            "required": [
                "report_time",
                "temperature",
                "humidity",
                "wind_speed",
                "cloud_cover",
                "rain",
                "fog",
            ],
        }
        props = schema["properties"] = {}
        props["report_time"] = {
            "description": "The time the report was made",
            "type": "string",
            "format": "date-time",
        }
        props["forecast_time"] = {
            "description": "The time the forecast is for (only for forecasts)",
            "type": "string",
            "format": "date-time",
        }
        props["temperature"] = {
            "description": "Temperature in Celsius",
            "type": "number",
        }
        props["humidity"] = {
            "description": "Humidity percentage",
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        }
        props["wind_speed"] = {
            "description": "Wind speed in m/s",
            "type": "number",
            "minimum": 0,
        }
        props["cloud_cover"] = {
            "description": "Cloud cover percentage",
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        }
        props["rain"] = {"description": "Whether it is raining", "type": "boolean"}
        props["fog"] = {"description": "Whether it is foggy", "type": "boolean"}
        return schema
