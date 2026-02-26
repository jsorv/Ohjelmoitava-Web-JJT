from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from weatherradar.models import WeatherReport


class ForecastConverter(BaseConverter):
    """Custom URL converter to fetch WeatherReport forecasts by ID."""

    def to_python(self, value):
        try:
            report_id = int(value)
        except ValueError:
            raise NotFound(description="Invalid forecast ID format")

        forecast = WeatherReport.query.filter_by(
            report_id=report_id, entry_type="forecast"
        ).first()
        if not forecast:
            raise NotFound(description="Forecast not found")
        return forecast

    def to_url(self, value):
        return str(value.report_id)
