"""Script to populate the database with sample data for testing."""

from datetime import datetime, timedelta
from ..weatherradar import db, create_app


def create_location(
    country: str, city: str, latitude: float, longitude: float
) -> "Location":
    """Creates a location if it doesn't exist, otherwise returns the existing one."""
    loc = Location.query.filter_by(country=country, city=city).first()
    if loc:
        return loc
    loc = Location(country=country, city=city, latitude=latitude, longitude=longitude)
    db.session.add(loc)
    db.session.commit()
    return loc


def add_weather_report(
    location: "Location",
    entry_type: str,
    report_time: datetime,
    forecast_time: datetime | None,
    temperature: float,
    humidity: int,
    wind_speed: float,
    cloud_cover: int,
    rain: bool,
    fog: bool,
) -> "WeatherReport":
    """Adds a weather report to the database."""
    report = WeatherReport(
        location_id=location.location_id,
        entry_type=entry_type,
        report_time=report_time,
        forecast_time=forecast_time,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        cloud_cover=cloud_cover,
        rain=rain,
        fog=fog,
    )
    db.session.add(report)
    db.session.commit()
    return report


if __name__ == "__main__":
    app = create_app()
    # Ensure models are imported after the app (and db) are available
    from ..weatherradar import models

    Location = models.Location
    WeatherReport = models.WeatherReport

    context = app.app_context()
    context.push()
    db.create_all()
    context.pop()
    with app.app_context():
        oulu = create_location("Finland", "Oulu", 65.0121, 25.4651)
        helsinki = create_location("Finland", "Helsinki", 60.1699, 24.9384)
        tampere = create_location("Finland", "Tampere", 61.4978, 23.7610)

        now = datetime.now()

        add_weather_report(
            helsinki, "report", now, None, 5.2, 75, 3.5, 40, False, False
        )
        add_weather_report(tampere, "report", now, None, 3.1, 85, 2.2, 60, False, True)
        add_weather_report(oulu, "report", now, None, -2.5, 90, 1.0, 80, True, True)
        add_weather_report(
            helsinki,
            "forecast",
            now,
            now + timedelta(hours=6),
            4.0,
            80,
            4.0,
            50,
            True,
            False,
        )
        add_weather_report(
            tampere,
            "forecast",
            now,
            now + timedelta(hours=6),
            2.0,
            90,
            3.0,
            70,
            False,
            False,
        )
        add_weather_report(
            oulu,
            "forecast",
            now,
            now + timedelta(hours=6),
            -3.5,
            95,
            2.5,
            90,
            True,
            True,
        )

        print(
            "Populate complete:",
            Location.query.count(),
            "locations;",
            WeatherReport.query.count(),
            "reports",
        )
