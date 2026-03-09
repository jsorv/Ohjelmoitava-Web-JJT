"""Utility functions and classes for the Weather Radar API."""

from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter


class LocationConverter(BaseConverter):
    """Custom URL converter to fetch Location objects by their ID."""

    def to_python(self, value):
        """Fetches a Location object by its location_id."""
        from .models import Location

        try:
            location_id = int(value)
        except ValueError as exc:
            raise NotFound(description="Invalid location ID format") from exc

        location = Location.query.filter_by(location_id=location_id).first()
        if not location:
            raise NotFound(description="Location not found")
        return location

    def to_url(self, value):
        """Converts a Location object back to a URL component."""
        return str(value.location_id)


class ForecastConverter(BaseConverter):
    """Custom URL converter to fetch WeatherReport forecasts by ID."""

    def to_python(self, value):
        """Fetches a WeatherReport forecast by its report_id."""
        from .models import WeatherReport

        try:
            report_id = int(value)
        except ValueError as exc:
            raise NotFound(description="Invalid forecast ID format") from exc

        forecast = WeatherReport.query.filter_by(
            report_id=report_id, entry_type="forecast"
        ).first()
        if not forecast:
            raise NotFound(description="Forecast not found")
        return forecast

    def to_url(self, value):
        """Converts a WeatherReport object back to a URL component."""
        return str(value.report_id)


class ReportConverter(BaseConverter):
    """Custom URL converter to fetch WeatherReport reports by ID."""

    def to_python(self, value):
        """Fetches a WeatherReport report by its report_id."""
        from .models import WeatherReport

        try:
            report_id = int(value)
        except ValueError as exc:
            raise NotFound(description="Invalid report ID format") from exc

        report = WeatherReport.query.filter_by(
            report_id=report_id, entry_type="report"
        ).first()
        if not report:
            raise NotFound(description="Report not found")
        return report

    def to_url(self, value):
        """Converts a WeatherReport object back to a URL component."""
        return str(value.report_id)
