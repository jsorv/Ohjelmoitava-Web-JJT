from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask("WeatherApp")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Location(db.Model):
    __tablename__ = "locations"
    __table_args__ = (db.UniqueConstraint("country", "city", name="uq_country_city"),)

    location_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(64), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    weather_reports = db.relationship(
        "WeatherReport",
        back_populates="location",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Location {self.city}, {self.country}>"

class WeatherReport(db.Model):
    __tablename__ = "weather_reports"

    report_id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.location_id"), nullable=False)

    entry_type = db.Column(db.Enum("report", "forecast", name="entry_type_enum"),nullable=False) # "report" or "forecast"

    report_time = db.Column(db.DateTime, nullable=False)
    forecast_time = db.Column(db.DateTime, nullable=True) # nullable true

    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Integer,db.CheckConstraint("humidity BETWEEN 0 AND 100"))
    wind_speed = db.Column(db.Float,db.CheckConstraint("wind_speed >= 0"))
    cloud_cover = db.Column(db.Integer,db.CheckConstraint("cloud_cover BETWEEN 0 AND 100"))
    rain = db.Column(db.Boolean, nullable=False)
    fog = db.Column(db.Boolean, nullable=False)

    location = db.relationship(
        "Location",
        back_populates="weather_reports"
    )

    def __repr__(self):
        return f"<WeatherReport {self.entry_type} for {self.location.id} at {self.report_time}>"
