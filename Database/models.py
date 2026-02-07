from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# from ? import db

class Location(db.Model):
    __tablename__ = "locations"

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

class WeatherReport(db.Model):
    __tablename__ = "weather_reports"

    report_id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"), nullable=False)

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

